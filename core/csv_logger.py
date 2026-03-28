import csv
import os


class CSVLogger:
    def __init__(self, log_dir="logs", filename="rep_history.csv"):
        self.log_dir = log_dir
        self.filepath = os.path.join(log_dir, filename)

        os.makedirs(self.log_dir, exist_ok=True)
        self._ensure_header()

    def _ensure_header(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "session_id",
                    "timestamp",
                    "rep_number",
                    "score",
                    "movement_bias",
                    "min_knee_angle",
                    "max_torso_angle",
                    "max_shin_angle",
                    "depth_ok",
                    "distance_status",
                    "feedback_1",
                    "feedback_2",
                    "feedback_3",
                ])

    def log_rep(self, rep_data: dict):
        feedback = rep_data.get("feedback", [])

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                rep_data.get("session_id", ""),
                rep_data.get("timestamp", ""),
                rep_data.get("rep_number", ""),
                rep_data.get("score", ""),
                rep_data.get("movement_bias", ""),
                rep_data.get("min_knee_angle", ""),
                rep_data.get("max_torso_angle", ""),
                rep_data.get("max_shin_angle", ""),
                rep_data.get("depth_ok", ""),
                rep_data.get("distance_status", ""),
                feedback[0] if len(feedback) > 0 else "",
                feedback[1] if len(feedback) > 1 else "",
                feedback[2] if len(feedback) > 2 else "",
            ])