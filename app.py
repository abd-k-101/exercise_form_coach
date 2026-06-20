import cv2
import os
import time
from datetime import datetime

from config import WINDOW_NAME, SMOOTHING_ALPHA, POSE_MODEL_PATH, POSE_NUM_POSES
from core.pose_estimator import PoseEstimator
from core.landmark_smoother import LandmarkSmoother
from core.csv_logger import CSVLogger
from exercise.squat_analyzer import SquatAnalyzer
from ui.overlay import draw_analysis
from core.audio_manager import AudioManager


def main():
    VIDEO_SOURCE = "demo_videos/squat_sample.mp4"
    source = VIDEO_SOURCE if os.path.isfile(VIDEO_SOURCE) else 0
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    session_id = datetime.now().strftime("sess_%Y%m%d_%H%M%S")

    logger = CSVLogger()
    pose_estimator = PoseEstimator(
        model_path=POSE_MODEL_PATH,
        num_poses=POSE_NUM_POSES,
    )
    smoother = LandmarkSmoother(alpha=SMOOTHING_ALPHA)
    analyzer = SquatAnalyzer(session_id=session_id)

    audio = AudioManager()
    audio.load("success", "assets/sounds/success.wav")
    audio.load("alert",   "assets/sounds/alert.wav")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vid_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    out = cv2.VideoWriter(
        'logs/annotated_demo.mp4',
        cv2.VideoWriter_fourcc(*'mp4v'),
        vid_fps,
        (width, height),
    )

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    fps = 0.0
    fps_frame_count = 0
    fps_window_start = time.perf_counter()
    start_time = time.perf_counter()

    while True:
        fps_frame_count += 1
        now = time.perf_counter()
        if now - fps_window_start >= 1.0:
            fps = fps_frame_count / (now - fps_window_start)
            fps_frame_count = 0
            fps_window_start = now

        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        timestamp_ms = int((time.perf_counter() - start_time) * 1000)

        landmarks, _ = pose_estimator.process(frame, timestamp_ms)

        if landmarks:
            smoothed_landmarks = smoother.smooth(landmarks)
            analysis = analyzer.analyze(smoothed_landmarks)
            pose_estimator.draw_pose(frame, smoothed_landmarks)
        else:
            analysis = analyzer.analyze({})

        if analysis.distance_status and analysis.distance_status.message != "Perfect distance":
            audio.speak(analysis.distance_status.message)
        elif analysis.phase == "NO_POSE" and analysis.live_feedback:    
            audio.speak(analysis.live_feedback[0])
        elif analysis.rep_event is not None and analysis.rep_event.get("feedback"):
            audio.speak(analysis.rep_event["feedback"][0])

        if analysis.rep_event is not None:
            logger.log_rep(analysis.rep_event)
            audio.play("success" if analysis.rep_event.get("score", 0) >= 70 else "alert")

        draw_analysis(frame, analysis, fps)
        out.write(frame)

        scale = 800 / height
        new_width = int(width * scale)
        display_frame = cv2.resize(frame, (new_width, 800))
        cv2.imshow(WINDOW_NAME, display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()