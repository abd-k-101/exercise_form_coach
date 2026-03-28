from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from core.geometry import calculate_angle, line_angle_from_vertical
from models.pose_landmarks import PoseLandmarkDict, RepFeedback, DistanceStatus


@dataclass
class SquatAnalysisResult:
    phase: str = "NO_POSE"
    rep_count: int = 0
    knee_angle: float = 0.0
    hip_angle: float = 0.0
    torso_angle: float = 0.0
    shin_angle: float = 0.0
    live_movement_bias: str = "Unknown"
    distance_status: Optional[DistanceStatus] = None
    last_rep_feedback: Optional[RepFeedback] = None
    live_feedback: List[str] = field(default_factory=list)
    rep_event: Optional[dict] = None


class SquatAnalyzer:
    def __init__(
        self,
        session_id,
        standing_knee_angle=160,
        bottom_knee_angle=100,
        shallow_knee_angle=110,
    ):
        self.session_id = session_id
        self.standing_knee_angle = standing_knee_angle
        self.bottom_knee_angle = bottom_knee_angle
        self.shallow_knee_angle = shallow_knee_angle

        self.phase = "STANDING"
        self.rep_count = 0
        self.reached_bottom = False
        self.prev_hip_y = None

        self.rep_active = False
        self.current_rep_min_knee_angle = None
        self.current_rep_max_torso_angle = None
        self.current_rep_max_shin_angle = None
        self.current_rep_distance_status = "Unknown"

        self.last_rep_feedback = None

    def _select_side(self, landmarks: PoseLandmarkDict, min_visibility=0.5):
        left = [
            landmarks.get("left_shoulder"),
            landmarks.get("left_hip"),
            landmarks.get("left_knee"),
            landmarks.get("left_ankle"),
        ]
        right = [
            landmarks.get("right_shoulder"),
            landmarks.get("right_hip"),
            landmarks.get("right_knee"),
            landmarks.get("right_ankle"),
        ]

        left_score = sum(1 for p in left if p and p.visibility >= min_visibility)
        right_score = sum(1 for p in right if p and p.visibility >= min_visibility)

        if left_score >= right_score and left_score >= 4:
            return "left"
        if right_score >= 4:
            return "right"
        return None

    def analyze(self, landmarks: PoseLandmarkDict):
        result = SquatAnalysisResult(rep_count=self.rep_count)

        side = self._select_side(landmarks)
        if side is None:
            result.phase = "NO_POSE"
            result.live_feedback = ["Ensure full side body is visible."]
            result.last_rep_feedback = self.last_rep_feedback
            return result

        shoulder = landmarks[f"{side}_shoulder"]
        hip = landmarks[f"{side}_hip"]
        knee = landmarks[f"{side}_knee"]
        ankle = landmarks[f"{side}_ankle"]

        shoulder_xy = shoulder.xy
        hip_xy = hip.xy
        knee_xy = knee.xy
        ankle_xy = ankle.xy

        knee_angle = calculate_angle(hip_xy, knee_xy, ankle_xy)
        hip_angle = calculate_angle(shoulder_xy, hip_xy, knee_xy)
        torso_angle = line_angle_from_vertical(hip_xy, shoulder_xy)
        shin_angle = line_angle_from_vertical(ankle_xy, knee_xy)

        distance_status = self._estimate_distance_status(landmarks)

        phase, rep_just_completed = self._detect_phase_and_rep_completion(
            knee_angle=knee_angle,
            hip_y=hip_xy[1],
        )

        self._update_rep_tracking(
            phase=phase,
            knee_angle=knee_angle,
            torso_angle=torso_angle,
            shin_angle=shin_angle,
            distance_status=distance_status.message,
        )

        rep_event = None
        if rep_just_completed:
            rep_event = self._finalize_rep_feedback()

        result.phase = phase
        result.rep_count = self.rep_count
        result.knee_angle = round(knee_angle, 1)
        result.hip_angle = round(hip_angle, 1)
        result.torso_angle = round(torso_angle, 1)
        result.shin_angle = round(shin_angle, 1)
        result.live_movement_bias = self._infer_bias(torso_angle, shin_angle)
        result.distance_status = distance_status
        result.last_rep_feedback = self.last_rep_feedback
        result.live_feedback = self._generate_live_feedback(phase)
        result.rep_event = rep_event

        return result

    def _detect_phase_and_rep_completion(self, knee_angle, hip_y):
        phase = self.phase
        rep_just_completed = False

        if self.prev_hip_y is None:
            self.prev_hip_y = hip_y

        moving_down = hip_y > self.prev_hip_y + 0.002
        moving_up = hip_y < self.prev_hip_y - 0.002

        if knee_angle > self.standing_knee_angle:
            if self.reached_bottom and phase == "ASCENDING":
                self.rep_count += 1
                self.reached_bottom = False
                rep_just_completed = True
            phase = "STANDING"

        elif knee_angle < self.bottom_knee_angle:
            phase = "BOTTOM"
            self.reached_bottom = True

        else:
            if moving_down:
                phase = "DESCENDING"
            elif moving_up:
                phase = "ASCENDING"

        self.prev_hip_y = hip_y
        self.phase = phase
        return phase, rep_just_completed

    def _update_rep_tracking(self, phase, knee_angle, torso_angle, shin_angle, distance_status):
        if phase in ["DESCENDING", "BOTTOM", "ASCENDING"]:
            if not self.rep_active:
                self.rep_active = True
                self.current_rep_min_knee_angle = knee_angle
                self.current_rep_max_torso_angle = torso_angle
                self.current_rep_max_shin_angle = shin_angle
                self.current_rep_distance_status = distance_status
            else:
                self.current_rep_min_knee_angle = min(self.current_rep_min_knee_angle, knee_angle)
                self.current_rep_max_torso_angle = max(self.current_rep_max_torso_angle, torso_angle)
                self.current_rep_max_shin_angle = max(self.current_rep_max_shin_angle, shin_angle)
                self.current_rep_distance_status = distance_status

    def _finalize_rep_feedback(self):
        if not self.rep_active:
            return None

        min_knee = round(self.current_rep_min_knee_angle, 1)
        max_torso = round(self.current_rep_max_torso_angle, 1)
        max_shin = round(self.current_rep_max_shin_angle, 1)
        depth_ok = min_knee <= self.shallow_knee_angle

        feedback = []

        if min_knee > self.shallow_knee_angle:
            feedback.append("Go a little deeper on the next rep.")

        if max_torso < 12:
            feedback.append("Sit your hips back more to improve hip hinge.")

        if max_shin > 30:
            feedback.append("Your knees are traveling too far forward.")

        if max_torso > 40:
            feedback.append("Keep your chest from collapsing too much.")

        if not feedback:
            feedback.append("Good rep. Keep it controlled.")

        movement_bias = self._infer_bias(max_torso, max_shin)
        score = self._score_rep(feedback)

        self.last_rep_feedback = RepFeedback(
            rep_index=self.rep_count,
            score=score,
            movement_bias=movement_bias,
            min_knee_angle=min_knee,
            max_torso_angle=max_torso,
            max_shin_angle=max_shin,
            depth_ok=depth_ok,
            feedback=feedback[:3],
        )

        rep_event = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "rep_number": self.rep_count,
            "score": score,
            "movement_bias": movement_bias,
            "min_knee_angle": min_knee,
            "max_torso_angle": max_torso,
            "max_shin_angle": max_shin,
            "depth_ok": depth_ok,
            "distance_status": self.current_rep_distance_status,
            "feedback": feedback[:3],
        }

        self.rep_active = False
        self.current_rep_min_knee_angle = None
        self.current_rep_max_torso_angle = None
        self.current_rep_max_shin_angle = None
        self.current_rep_distance_status = "Unknown"

        return rep_event

    def _infer_bias(self, torso_angle, shin_angle):
        if shin_angle > 28 and torso_angle < 14:
            return "Quad-biased"
        elif torso_angle > 18 and shin_angle < 25:
            return "Glute-biased"
        return "Balanced"

    def _score_rep(self, feedback):
        score = 100
        for item in feedback:
            lower = item.lower()
            if "deeper" in lower:
                score -= 20
            elif "hips back" in lower:
                score -= 15
            elif "knees are traveling too far forward" in lower:
                score -= 15
            elif "chest" in lower:
                score -= 15
        return max(0, score)

    def _generate_live_feedback(self, phase):
        if phase == "DESCENDING":
            return ["Lower with control."]
        if phase == "BOTTOM":
            return ["Drive up with balance."]
        if phase == "ASCENDING":
            return ["Finish the rep strong."]
        if phase == "STANDING":
            return ["Ready for next rep."]
        return ["Ensure full side body is visible."]

    def _estimate_distance_status(self, landmarks: PoseLandmarkDict):
        visible_points = [p for p in landmarks.values() if p is not None]
        if len(visible_points) < 4:
            return DistanceStatus("Adjust camera position", (0, 0, 255))

        ys = [p.y for p in visible_points]
        body_height = max(ys) - min(ys)

        if body_height < 0.45:
            return DistanceStatus("Move closer", (0, 0, 255))
        elif body_height > 0.85:
            return DistanceStatus("Move away", (0, 0, 255))
        return DistanceStatus("Perfect distance", (0, 255, 0))