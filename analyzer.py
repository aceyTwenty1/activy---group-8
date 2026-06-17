import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import urllib.request
from exercise_repo import get_exercise_profile

class VisualExerciseAnalyzer:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(dir_path, 'pose_landmarker_full.task')
        
        if not os.path.exists(model_path):
            print("Downloading 'pose_landmarker_full.task'...")
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

    def process_and_draw_video(self, video_path, output_path, exercise_name):
        profile = get_exercise_profile(exercise_name)
        if not profile:
            print(f"[!] Error: Exercise profile '{exercise_name}' not found.")
            return

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[!] Error: Could not open video {video_path}")
            return

        # Gather video properties for the exporter
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        
        # Configure video writer to output the finalized visual clip
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        j_map = profile["tracking_joints"]
        print(f"Analyzing and drawing visual skeleton rig for: {exercise_name}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert frame for MediaPipe tracking pass
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.detector.detect(mp_image)
            
            if detection_result.pose_landmarks:
                landmarks = detection_result.pose_landmarks[0]
                
                # Convert normalized landmarks into actual pixel locations
                points = {}
                for joint_name, idx in j_map.items():
                    lm = landmarks[idx]
                    points[joint_name] = (int(lm.x * width), int(lm.y * height))

                # Default tracking color is Green (Good Form)
                rig_color = (0, 255, 0) # BGR Format
                status_text = "FORM STATUS: STABLE"

                # Run biomechanical threshold checking rules
                if "hip" in points and "knee" in points and "ankle" in points:
                    knee_angle = self.calculate_angle(points["hip"], points["knee"], points["ankle"])
                    
                    # Squat depth checking example mapping rule from repo
                    if exercise_name == "squat" and knee_angle > profile["checks"]["depth"]["limit"]:
                        # If a user is at the bottom but shallow, paint the rig red
                        if points["hip"][1] > (height * 0.6): 
                            rig_color = (0, 0, 255) # Red alert color
                            status_text = f"WARNING: {profile['checks']['depth']['fail_cue']}"

                # Draw the tracking bones onto the frame layout
                if "hip" in points and "knee" in points:
                    cv2.line(frame, points["hip"], points["knee"], rig_color, 4)
                if "knee" in points and "ankle" in points:
                    cv2.line(frame, points["knee"], points["ankle"], rig_color, 4)
                if "shoulder" in points and "hip" in points:
                    cv2.line(frame, points["shoulder"], points["hip"], rig_color, 4)

                # Draw joint tracker nodes
                for joint_name, coord in points.items():
                    cv2.circle(frame, coord, 6, (255, 255, 255), -1)

                # Superimpose dashboard alerts onto the visual top-bar header
                cv2.putText(frame, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, rig_color, 2)

            # Save the frame into our output video asset file
            out.write(frame)

        cap.release()
        out.release()
        print(f"[✓] Processing complete! Asset saved as: {output_path}")

if __name__ == "__main__":
    analyzer = VisualExerciseAnalyzer()
    
    video_input = "uploaded_workout_sample.mp4"
    video_output = "output_analyzed_workout.mp4"
    exercise = "squat"
    
    if os.path.exists(video_input):
        analyzer.process_and_draw_video(video_input, video_output, exercise)
    else:
        print(f"[!] Please place an input video named '{video_input}' inside this folder to generate the visual rig.")