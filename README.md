Here is the fully updated, highly professional `README.md` reflecting all the new enterprise-grade features (TTS audio, video exporting, testing, and UI scaling).

```md
# 🏋️‍♂️ Exercise Form Coach: AI-Powered Squat Analyzer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Tasks_API-orange)
![Pytest](https://img.shields.io/badge/Pytest-Passing-success)

An intelligent, real-time computer vision application that tracks body mechanics, counts repetitions, and scores squat form using the **MediaPipe Tasks Vision API** and **OpenCV**. 

Unlike simple rep counters, this application acts as a virtual coach. It analyzes your joint angles, assesses depth, evaluates movement bias, and provides actionable, real-time visual and **vocal** feedback.

---

## ✨ Key Features

* **Real-Time Pose Tracking:** Utilizes the lightweight MediaPipe Pose Landmarker model to track the human skeleton in real-time via webcam or pre-recorded video.
* **Asynchronous Voice Coaching:** Features a threaded Text-to-Speech (TTS) engine that verbally guides you into the frame and reads out your form corrections after a set without dropping video frames.
* **Intelligent Form Analysis:** Calculates precise kinematic metrics (knee flexion, hip flexion, torso lean, shin angle) to evaluate squat depth, forward knee travel, and chest collapse.
* **Automated Video Export:** Automatically captures and exports your session as an `annotated_demo.mp4` file with all AI skeletal tracking and text overlays applied.
* **Smart UI Scaling:** Dynamically scales high-resolution portrait videos to fit your screen while adding high-contrast black strokes to text for perfect readability on any background.
* **Telemetry & Session Logging:** Exports detailed, rep-by-rep performance data (kinematic maximums/minimums, scores, and specific feedback) to a CSV file (`logs/rep_history.csv`).
* **Jitter Reduction & Optimization:** Implements an Exponential Moving Average (EMA) filter to stabilize joint coordinates and includes a live FPS counter to monitor system performance.

---

## 🏗️ Project Architecture

The codebase is highly modular, separating the AI inference, mathematical calculations, business logic, and UI rendering.

```text
exercise_form_coach/
├── app.py                     # Main application entry point and OpenCV loop
├── config.py                  # Global configuration (thresholds, scaling, UI constants)
├── core/
│   ├── pose_estimator.py      # Wrapper for MediaPipe Tasks Vision API
│   ├── geometry.py            # Mathematical functions for calculating joint angles
│   ├── landmark_smoother.py   # EMA filter for coordinate stabilization
│   ├── audio_manager.py       # Asynchronous TTS and sound effect engine
│   └── csv_logger.py          # Utility for logging session data to CSV
├── exercise/
│   └── squat_analyzer.py      # State machine: counts reps, assesses form, generates feedback
├── models/
│   └── pose_landmarks.py      # Strictly typed Dataclasses for data structures
├── demo_videos/               # Drop 'squat_sample.mp4' here for instant testing
├── logs/                      # Output directory for CSV telemetry and MP4 exports
├── tests/                     # Pytest suite for geometry and mathematical assertions
└── ui/
    └── overlay.py             # OpenCV rendering logic for skeletons, angles, and UI

```

---

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have Python 3.8+ installed. Linux users may need to install the `espeak` driver for the Text-to-Speech engine:

```bash
sudo apt-get install espeak

```

### 2. Installation

Clone the repository, set up a virtual environment, and install the dependencies:

```bash
git clone [https://github.com/yourusername/exercise_form_coach.git](https://github.com/yourusername/exercise_form_coach.git)
cd exercise_form_coach
python -m venv ex_env
source ex_env/bin/activate  # On Windows: `ex_env\Scripts\activate`
pip install opencv-python mediapipe pygame pyttsx3 pytest

```

### 3. Download the MediaPipe Model

The application relies on the MediaPipe Pose Landmarker task file:

1. Download the `pose_landmarker_heavy.task` from the [Official MediaPipe Portal](https://www.google.com/search?q=https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/index%23models).
2. Rename the file to `pose_landmarker.task`.
3. Place it inside the `models_store/` directory.

---

## 🎮 Usage

### Running with a Webcam

Simply execute the main script. Stand back so your entire side profile (shoulder to ankle) is visible.

```bash
python app.py

```

### Running with a Demo Video (Testing Mode)

To test the pipeline without standing up:

1. Download a side-profile squat video (e.g., from Pexels or Pixabay).
2. Rename it to `squat_sample.mp4` and place it in the `demo_videos/` directory.
3. Run `python app.py`. The system will automatically detect the video, process it, and output the annotated result to `logs/annotated_demo.mp4`.

---

## ⚙️ Configuration & Strictness Tuning

You can easily tweak the AI's strictness and UI in `config.py`:

* **Squat Strictness:** Adjust `BOTTOM_KNEE_ANGLE` and `SHALLOW_KNEE_ANGLE`. Lower values (e.g., 85°) require strict powerlifting depth, while higher values (e.g., 100°) are better for general fitness tracking.
* **`SMOOTHING_ALPHA`**: Adjusts the EMA filter. Lower values = smoother tracking but slightly more lag.
* **Visuals:** Adjust `FONT_SCALE` and `THICKNESS` to accommodate different display resolutions.

---

## 🧪 Testing

This project embraces Test-Driven Development (TDD) for its core mathematical calculations. To run the test suite:

```bash
pytest tests/ -v

```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! To add a new exercise (e.g., Deadlift, Bench Press), simply create a new analyzer class in the `exercise/` directory following the modular blueprint of `squat_analyzer.py`.

```

```
