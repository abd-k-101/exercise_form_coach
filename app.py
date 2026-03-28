import cv2
import time
from datetime import datetime

from config import WINDOW_NAME, SMOOTHING_ALPHA, POSE_MODEL_PATH, POSE_NUM_POSES
from core.pose_estimator import PoseEstimator
from core.landmark_smoother import LandmarkSmoother
from core.csv_logger import CSVLogger
from exercise.squat_analyzer import SquatAnalyzer
from ui.overlay import draw_analysis


def main():
    cap = cv2.VideoCapture(0)
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

    start_time = time.perf_counter()

    while True:
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

        if analysis.rep_event is not None:
            logger.log_rep(analysis.rep_event)

        draw_analysis(frame, analysis)
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()