import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import time
import csv
import os
from datetime import datetime

# --- 1. ROBUST VOICE ENGINE ---
# We initialize it globally. If it fails, we print the error but don't crash.
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150) # Slower = clearer
except:
    print("⚠️ WARNING: Voice engine could not start.")
    engine = None

def speak(text):
    print(f"🗣️ AI SAYS: {text}") # Visual backup in terminal
    if engine:
        # We use a lightweight thread to avoid freezing the video
        def _speak():
            try:
                # Re-initialize for thread safety on some Windows versions
                local_engine = pyttsx3.init() 
                local_engine.say(text)
                local_engine.runAndWait()
            except: 
                pass
        threading.Thread(target=_speak, daemon=True).start()

# --- CONFIGURATION ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
COLOR_GOOD = (0, 255, 0)
COLOR_BAD = (0, 0, 255)

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360-angle
    return angle

# --- CAMERA SETUP ---
cap = cv2.VideoCapture(0) # Try 0 first. If black screen, change to 1.
if not cap.isOpened():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("🚨 ERROR: No camera found.")
        exit()

# --- GLOBALS ---
good_reps = 0
bad_reps = 0
mode = "SQUAT"
feedback = "Stand in frame"
workout_log = [] 
stage = "UP" 
min_angle_during_rep = 180

print("--- DEBUG MODE STARTED ---")
print("Press 's' for Squat, 'c' for Curl.")
print("Press 'q' to Quit and Save.")

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    speak("System Online")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: continue

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # KEYBOARD
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'): break
        if key == ord('s'): mode = "SQUAT"; stage = "UP"; speak("Squat Mode")
        if key == ord('c'): mode = "CURL"; stage = "DOWN"; speak("Curl Mode")

        try:
            landmarks = results.pose_landmarks.landmark
            
            # Get Joints
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            angle = 0
            
            # --- LOGIC: SQUAT ---
            if mode == "SQUAT":
                angle = calculate_angle(hip, knee, ankle)
                
                # Debug Print every 20 frames to avoid spamming
                # if int(time.time() * 10) % 10 == 0: print(f"Squat Angle: {int(angle)} | Stage: {stage}")

                # 1. Going Down
                if angle < 160: 
                    if angle < min_angle_during_rep:
                        min_angle_during_rep = angle
                    if angle < 150:
                        stage = "DOWN"

                # 2. Standing Up (Check Rep)
                if angle > 165 and stage == "DOWN":
                    stage = "UP"
                    print(f"📝 Rep Finished! Lowest Angle: {int(min_angle_during_rep)}")
                    
                    if min_angle_during_rep < 95: # Slightly easier depth
                        good_reps += 1
                        feedback = "PERFECT"
                        speak("Good")
                        workout_log.append([datetime.now().strftime("%H:%M:%S"), mode, "RIGHT", "Good Depth"])
                    else:
                        bad_reps += 1
                        feedback = "TOO SHALLOW"
                        speak("Go Lower")
                        workout_log.append([datetime.now().strftime("%H:%M:%S"), mode, "WRONG", f"Depth: {int(min_angle_during_rep)}"])
                    
                    min_angle_during_rep = 180

            # --- LOGIC: CURL ---
            elif mode == "CURL":
                angle = calculate_angle(shoulder, elbow, wrist)
                
                # 1. Going Up (Squeeze)
                if angle < 150:
                    if angle < min_angle_during_rep:
                        min_angle_during_rep = angle
                    stage = "UP"

                # 2. Going Down (Extension)
                if angle > 160 and stage == "UP":
                    stage = "DOWN"
                    print(f"📝 Rep Finished! Peak Angle: {int(min_angle_during_rep)}")

                    if min_angle_during_rep < 40:
                        good_reps += 1
                        feedback = "GOOD SQUEEZE"
                        speak("Good")
                        workout_log.append([datetime.now().strftime("%H:%M:%S"), mode, "RIGHT", "Full ROM"])
                    else:
                        bad_reps += 1
                        feedback = "HALF REP"
                        speak("All the way up")
                        workout_log.append([datetime.now().strftime("%H:%M:%S"), mode, "WRONG", "Half Rep"])

                    min_angle_during_rep = 180

            # Draw Interface
            cv2.rectangle(image, (0,0), (640,100), (40,40,40), -1)
            cv2.putText(image, f"GOOD: {good_reps}", (20,80), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_GOOD, 2)
            cv2.putText(image, f"BAD: {bad_reps}", (250,80), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_BAD, 2)
            cv2.putText(image, feedback, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            
            # Skeleton
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        except Exception as e:
            # print(f"Error in loop: {e}") 
            pass
        
        cv2.imshow('LiftLogic DEBUG', image)

# --- SAVE EXCEL ---
print("--- CLOSING APP ---")
if len(workout_log) > 0:
    filename = f"Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Exercise", "Result", "Note"])
        writer.writerows(workout_log)
    
    # Get absolute path to show user where file is
    full_path = os.path.abspath(filename)
    print(f"✅ SUCCESS! Excel file saved at:\n{full_path}")
    speak("Data Saved")
else:
    print("⚠️ No reps were recorded, so no Excel file was created.")
    print("Tip: Make sure you complete the movement fully (Go down AND back up).")

cap.release()
cv2.destroyAllWindows()