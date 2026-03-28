import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from models.pose_landmarks import LandmarkPoint, PoseLandmarkDict


class PoseEstimator:
    """
    MediaPipe Tasks API wrapper for pose landmarking.
    Keeps MediaPipe-specific details isolated from the rest of the codebase.
    """

    def __init__(
        self,
        model_path: str,
        num_poses: int = 1,
        min_pose_detection_confidence: float = 0.5,
        min_pose_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        base_options = python.BaseOptions(model_asset_path=model_path)

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=num_poses,
            min_pose_detection_confidence=min_pose_detection_confidence,
            min_pose_presence_confidence=min_pose_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_segmentation_masks=False,
        )

        self.landmarker = vision.PoseLandmarker.create_from_options(options)

        # MediaPipe Pose landmark indices
        self.needed_indices = {
            "left_shoulder": 11,
            "right_shoulder": 12,
            "left_hip": 23,
            "right_hip": 24,
            "left_knee": 25,
            "right_knee": 26,
            "left_ankle": 27,
            "right_ankle": 28,
        }

        # Optional skeletal connections for manual drawing
        self.draw_connections = [
            ("left_shoulder", "left_hip"),
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("right_shoulder", "right_hip"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
            ("left_shoulder", "right_shoulder"),
            ("left_hip", "right_hip"),
        ]

    def process(self, frame_bgr, timestamp_ms: int):
        """
        Args:
            frame_bgr: OpenCV frame in BGR format
            timestamp_ms: monotonically increasing timestamp in ms

        Returns:
            landmarks_dict, raw_results
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        results = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        landmarks: PoseLandmarkDict = {}

        if not results.pose_landmarks:
            return landmarks, results

        pose = results.pose_landmarks[0]

        for name, idx in self.needed_indices.items():
            pt = pose[idx]
            visibility = getattr(pt, "visibility", 1.0)
            landmarks[name] = LandmarkPoint(
                x=pt.x,
                y=pt.y,
                visibility=visibility,
            )

        return landmarks, results

    def draw_pose(self, frame, landmarks: PoseLandmarkDict):
        """
        Manual draw method so the UI layer does not depend on removed legacy drawing utils.
        """
        if not landmarks:
            return

        h, w = frame.shape[:2]

        # Draw joints
        for point in landmarks.values():
            if point is None:
                continue
            cx, cy = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        # Draw simple skeleton
        for a_name, b_name in self.draw_connections:
            a = landmarks.get(a_name)
            b = landmarks.get(b_name)
            if a is None or b is None:
                continue

            ax, ay = int(a.x * w), int(a.y * h)
            bx, by = int(b.x * w), int(b.y * h)
            cv2.line(frame, (ax, ay), (bx, by), (255, 255, 0), 2)