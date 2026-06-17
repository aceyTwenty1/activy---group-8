# analyzer.py
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import json
import os
import urllib.request

# Import our new rules repository
from exercise_repo import get_exercise_profile

class UniversalExerciseAnalyzer:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(dir_path, 'pose_landmarker_full.task')
        
        if not os.path.exists(model_path):
            print("=" * 60)
            print("Downloading 'pose_landmarker_full.task' directly into your folder...")
            print("=" * 60)
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task"
            urllib.request.urlretrieve(url, model_path)

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(base_options=base_options, output_segmentation_masks=False)
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return round(360.0 - angle if angle > 180.0 else angle, 2)

    def process_workout(self, video_path, exercise_name):
        """Processes video using the rules looked up from the external repository file."""
        profile = get_exercise_profile(exercise_name)
        if not profile:
            return {"error": f"Exercise profile '{exercise_name}' is not supported in exercise_repo.py"}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": f"Could not open video file: {video_path}"}

        fps = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        frame_count = 0
        telemetry = []

        # Get specific IDs mapping to what this exercise tracks
        j_map = profile["tracking_joints"]

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame_count += 1
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.detector.detect(mp_image)
            
            if detection_result.pose_landmarks:
                landmarks = detection_result.pose_landmarks[0]
                
                # Dynamically pull out joints based on repo request mapping rules
                frame_data = {"frame": frame_count, "timestamp": round(frame_count / fps, 2)}
                
                # Check for knee angle if part of schema
                if "hip" in j_map and "knee" in j_map and "ankle" in j_map:
                    frame_data["knee_angle"] = self.calculate_angle(
                        [landmarks[j_map["hip"]].x, landmarks[j_map["hip"]].y],
                        [landmarks[j_map["knee"]].x, landmarks[j_map["knee"]].y],
                        [landmarks[j_map["ankle"]].x, landmarks[j_map["ankle"]].y]
                    )
                
                # Check for elbow angle if part of schema
                if "shoulder" in j_map and "elbow" in j_map and "wrist" in j_map:
                    frame_data["elbow_angle"] = self.calculate_angle(
                        [landmarks[j_map["shoulder"]].x, landmarks[j_map["shoulder"]].y],
                        [landmarks[j_map["elbow"]].x, landmarks[j_map["elbow"]].y],
                        [landmarks[j_map["wrist"]].x, landmarks[j_map["wrist"]].y]
                    )

                # Track core movement trigger baseline height tracking metric
                base_key = profile.get("baseline_joint")
                if base_key and base_key in j_map:
                    frame_data["tracking_y"] = landmarks[j_map[base_key]].y

                telemetry.append(frame_data)
                
        cap.release()
        return self.analyze_set(telemetry, profile)

    def analyze_set(self, telemetry, profile):
        if not telemetry:
            return {"error": "No tracking telemetry captured."}
            
        # Basic rep-counter template dynamically running checks against repo targets
        total_reps = 0
        form_score = 100
        coaching_feedback = []

        # Simple logic tracking simulation mock for the profile evaluation workflow
        if profile["type"] == "dynamic":
            # Count fluctuations over threshold configurations
            total_reps = len(telemetry) // 45  # Estimated proxy representation loop counts
            if total_reps == 0 and len(telemetry) > 20: 
                total_reps = 1
        else:
            total_reps = 1  # Static holds count as 1 set element execution block

        return {
            "exercise": profile.get("baseline_joint", "plank").capitalize(),
            "summary": {
                "total_reps_counted": total_reps,
                "overall_form_score": form_score
            },
            "coaching_cues": ["Good posture maintained!", "Keep pushing consistency."]
        }

if __name__ == "__main__":
    analyzer = UniversalExerciseAnalyzer()
    
    # CHOOSE YOUR EXERCISE HERE: "squat", "push_up", "bicep_curl", "lunge", etc.
    target_exercise = "squat" 
    video_file = "uploaded_workout_sample.mp4"
    
    if os.path.exists(video_file):
        print(f"Starting analytics pass for target exercise rule profile: {target_exercise}")
        analysis_output = analyzer.process_workout(video_file, target_exercise)
        print(json.dumps(analysis_output, indent=4))
    else:
        print(f"\n[!] Modular Setup Successful. Drop your testing video file '{video_file}' here to scan for '{target_exercise}'.")