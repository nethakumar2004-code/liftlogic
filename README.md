# 🏋️‍♂️ LiftLogic: AI Personal Trainer & Form Auditor

**An automated biomechanics auditing tool built with Computer Vision.**

> *"Strava tracks your run. LiftLogic audits your lift."*

[![Watch the Demo](https://img.shields.io/badge/Watch-Demo_Video-red?style=for-the-badge&logo=youtube)]([LINK TO YOUR VIDEO HERE])

## 💡 The Problem
Fitness apps today are great at tracking *what* you did (Sets/Reps), but terrible at tracking *how* you did it (Form/Velocity). Manual logging is outdated, and hiring a personal trainer is expensive.

## 🚀 The Solution
LiftLogic is a Python-based computer vision engine that turns any webcam into an AI Coach. It doesn't just count reps; it **audits** them in real-time using biomechanical thresholds.

### Key Features
* **🧠 Intelligent Audit Engine:** Distinguishes between **Valid Reps** (Full ROM) and **Cheat Reps** (Half-reps/Momentum) using dynamic angle calculation.
* **🗣️ Real-Time Voice Feedback:** Uses Text-to-Speech to correct form instantly (e.g., *"Go Lower"*, *"Don't Swing"*).
* **⚡ Velocity Based Training (VBT):** Measures the duration of the eccentric phase to detect if a user is controlling the weight or diving.
* **📊 Data Consultant Mode:** Automatically generates a granular `.csv` biomechanics report after every session, logging failure points and cheat frequency.

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Vision:** MediaPipe Pose (Google), OpenCV
* **Data Analysis:** NumPy, CSV
* **Audio:** Pyttsx3 (Text-to-Speech Engine)

## 💻 How to Run
1.  **Clone the repository**
    ```bash
    git clone [https://github.com/nethakumar2004-code/LiftLogic-AI-Trainer.git](https://github.com/nethakumar2004-code/LiftLogic-AI-Trainer.git)
    cd LiftLogic-AI-Trainer
    ```

2.  **Install Dependencies**
    ```bash
    pip install opencv-python mediapipe numpy pyttsx3
    ```

3.  **Run the Auditor**
    ```bash
    python main_audit.py
    ```

4.  **Controls**
    * Press `s` for **Squat Mode** (Depth Detection)
    * Press `c` for **Curl Mode** (Momentum & ROM Detection)
    * Press `q` to **Quit & Export Data**

## 📂 Data Export Example
The application generates a `Workout_Report.csv` file automatically. This raw data allows for deep analysis of athlete performance trends.

| Timestamp | Exercise | Result | Note |
| :--- | :--- | :--- | :--- |
| 10:42:05 | SQUAT | ✅ RIGHT | Good Depth |
| 10:42:12 | SQUAT | ❌ WRONG | Depth missed (Hit 110°) |
| 10:42:25 | CURL | ❌ WRONG | Momentum Detected |

---
*Built by Bharath | 2025*
*Open for Data Consultant & AI Engineering roles.*
