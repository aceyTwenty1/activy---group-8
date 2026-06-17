import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import json
import os
import urllib.request

class LungeAnalyzer:
    def __init__(self):
        # Dynamically locate the task file paths
        dir_path = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(dir_path, 'pose_landmarker_full.task')
        
        # AUTOMATIC DOWNLOAD: If the model file is missing, fetch it!
        if not os.path.exists(model_path):
            print("=" * 60)
            print("Downloading 'pose_landmarker_full.task' directly into your folder...")
            print("This is a one-time 15MB download. Please wait a moment...")
            print("=" * 60)
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task"
            urllib.request.urlretrieve(url, model_path)
            print("Download complete! Starting MediaPipe pipeline setup...\n")

        # Base configuration for the MediaPipe Tasks API
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def calculate_angle(self, a, b, c):
        """Calculates the angle at vertex 'b' given three points [x, y]."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360.0 - angle
            
        return round(angle, 2)

    def process_video(self, video_path):
        """Processes the uploaded video frame-by-frame and extracts analytics."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": f"Could not open video file: {video_path}"}

        fps = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        frame_count = 0
        telemetry = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Convert frame to RGB format and wrap it in a MediaPipe Image object
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Run the new MediaPipe Pose Landmarker detection loop
            detection_result = self.detector.detect(mp_image)
            
            if detection_result.pose_landmarks:
                # Extract landmarks for the first detected individual
                landmarks = detection_result.pose_landmarks[0]
                
                # MediaPipe landmark indices: Shoulder (11), Hip (23), Knee (25), Ankle (27), Toe (31)
                shoulder = [landmarks[11].x, landmarks[11].y]
                hip      = [landmarks[23].x, landmarks[23].y]
                knee     = [landmarks[25].x, landmarks[25].y]
                ankle    = [landmarks[27].x, landmarks[27].y]
                toe      = [landmarks[31].x, landmarks[31].y]

                # Trigonometry calculations
                knee_angle = self.calculate_angle(hip, knee, ankle)
                
                # Create a virtual vertical anchor directly above the hip to measure torso tilt
                vertical_anchor = [hip[0], hip[1] - 0.5]
                torso_angle = self.calculate_angle(shoulder, hip, vertical_anchor)
                
                # Check directional alignment (assuming movement profiles left-to-right)
                knee_past_toe = knee[0] > toe[0] if shoulder[0] < hip[0] else knee[0] < toe[0]

                telemetry.append({
                    "frame": frame_count,
                    "timestamp": round(frame_count / fps, 2),
                    "knee_angle": knee_angle,
                    "torso_angle": torso_angle,
                    "knee_past_toe": knee_past_toe,
                    "hip_y": hip[1]
                })
                
        cap.release()
        return self.analyze_telemetry(telemetry)

    def analyze_telemetry(self, telemetry):
        """Segments raw frame data into distinct reps and runs the logic checks."""
        if not telemetry:
            return {"error": "No motion telemetry captured from video."}

        reps = []
        state = "standing"  # States: standing, descending, ascending
        current_rep = None
        
        initial_hips = [f["hip_y"] for f in telemetry[:10]]
        standing_hip_baseline = np.mean(initial_hips) if initial_hips else 0.5
        
        for frame in telemetry:
            hip_y = frame["hip_y"]
            knee_angle = frame["knee_angle"]
            
            if state == "standing" and (hip_y - standing_hip_baseline) > 0.04:
                state = "descending"
                current_rep = {
                    "start_time": frame["timestamp"],
                    "min_knee_angle": 180.0,
                    "max_torso_lean": 0.0,
                    "knee_tracking_error": False
                }
                
            elif state == "descending":
                if knee_angle < current_rep["min_knee_angle"]:
                    current_rep["min_knee_angle"] = knee_angle
                    
                if frame["torso_angle"] > current_rep["max_torso_lean"]:
                    current_rep["max_torso_lean"] = frame["torso_angle"]
                    
                if frame["knee_past_toe"]:
                    current_rep["knee_tracking_error"] = True
                    
                if len(telemetry) > frame["frame"] and frame["hip_y"] < telemetry[frame["frame"]-2]["hip_y"]:
                    state = "ascending"
                    
            elif state == "ascending" and (standing_hip_baseline - hip_y) <= 0.02:
                state = "standing"
                current_rep["end_time"] = frame["timestamp"]
                reps.append(current_rep)
                current_rep = None

        feedback_log = []
        total_score_deductions = 0
        
        for idx, rep in enumerate(reps, 1):
            rep_errors = []
            
            if rep["min_knee_angle"] > 110:
                rep_errors.append("Low depth. Try dropping your hips lower until your thigh is parallel to the ground.")
                total_score_deductions += 10
            elif rep["min_knee_angle"] < 70:
                rep_errors.append("Extreme knee flexion. Avoid dropping too fast or too deep to protect the joint.")
                total_score_deductions += 5
                
            if rep["max_torso_lean"] > 15:
                rep_errors.append("Forward torso lean detected. Keep your chest proud and stack your shoulders over your hips.")
                total_score_deductions += 15
                
            if rep["knee_tracking_error"]:
                rep_errors.append("Knee shearing force. Do not let your front knee drift past your toes.")
                total_score_deductions += 15
                
            feedback_log.append({
                "rep_number": idx,
                "timestamp_seconds": rep["start_time"],
                "metrics": {
                    "peak_knee_flexion": rep["min_knee_angle"],
                    "peak_torso_lean": rep["max_torso_lean"]
                },
                "coaching_cues": rep_errors if rep_errors else ["Flawless form execution!"]
            })

        form_score = max(0, 100 - total_score_deductions)
        
        return {
            "summary": {
                "total_reps_counted": len(reps),
                "overall_form_score": form_score,
                "primary_improvement_target": self.get_primary_target(feedback_log)
            },
            "detailed_breakdown": feedback_log
        }

    def get_primary_target(self, feedback_log):
        all_cues = [cue for rep in feedback_log for cue in rep["coaching_cues"]]
        if not all_cues or "Flawless form execution!" in all_cues:
            return "Maintain current consistency. Ready to increase volume or load."
        return max(set(all_cues), key=all_cues.count)

if __name__ == "__main__":
    analyzer = LungeAnalyzer()
    # Check if a video exists to process, otherwise provide guidance
    video_file = "uploaded_workout_sample.mp4"
    if os.path.exists(video_file):
        analysis_output = analyzer.process_video(video_file)
        print(json.dumps(analysis_output, indent=4))
    else:
        print(f"\n[!] Setup Successful. To test your tracking engine fully, drop a lunge workout video named '{video_file}' into this folder.")