import cv2
import numpy as np
import mediapipe as mp
import json

class LungeAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

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
            return {"error": "Could not open video file."}

        fps = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        frame_count = 0
        telemetry = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            # Convert to RGB for MediaPipe processing
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Extract key joint coordinates
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hip      = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,      landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee     = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle    = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                toe      = [landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]

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
        
        # Analyze the timeline trend data to isolate repetitions and errors
        return self.analyze_telemetry(telemetry)

    def analyze_telemetry(self, telemetry):
        """Segments raw frame data into distinct reps and runs the logic checks."""
        if not telemetry:
            return {"error": "No motion telemetry captured from video."}

        reps = []
        state = "standing"  # States: standing, descending, ascending
        current_rep = None
        
        # Determine movement baseline threshold using the first few frames
        initial_hips = [f["hip_y"] for f in telemetry[:10]]
        standing_hip_baseline = np.mean(initial_hips) if initial_hips else 0.5
        
        for frame in telemetry:
            hip_y = frame["hip_y"]
            knee_angle = frame["knee_angle"]
            
            # State Machine to catch distinct lunges
            # Use parentheses for the walrus operator to ensure correct parsing
            if state == "standing" and (h_diff := (hip_y - standing_hip_baseline)) > 0.04:
                # User starts dropping lower down into the lunge
                state = "descending"
                current_rep = {
                    "start_time": frame["timestamp"],
                    "min_knee_angle": 180.0,
                    "max_torso_lean": 0.0,
                    "knee_tracking_error": False
                }
                
            elif state == "descending":
                # Track the lowest depth reached (minimum knee internal angle)
                if knee_angle < current_rep["min_knee_angle"]:
                    current_rep["min_knee_angle"] = knee_angle
                    
                if frame["torso_angle"] > current_rep["max_torso_lean"]:
                    current_rep["max_torso_lean"] = frame["torso_angle"]
                    
                if frame["knee_past_toe"]:
                    current_rep["knee_tracking_error"] = True
                    
                # Turnaround point: User starts driving back up
                # We notice hip_y reducing significantly compared to its previous trajectory
                if len(telemetry) > frame["frame"] and frame["hip_y"] < telemetry[frame["frame"]-2]["hip_y"]:
                    state = "ascending"
                    
            elif state == "ascending" and (standing_hip_baseline - hip_y) <= 0.02:
                # User returned safely back to standing baseline profile
                state = "standing"
                current_rep["end_time"] = frame["timestamp"]
                reps.append(current_rep)
                current_rep = None

        # Build the final diagnostic metrics JSON payload
        feedback_log = []
        total_score_deductions = 0
        
        for idx, rep in enumerate(reps, 1):
            rep_errors = []
            
            # Check 1: Lunge Depth Check
            if rep["min_knee_angle"] > 110:
                rep_errors.append("Low depth. Try dropping your hips lower until your thigh is parallel to the ground.")
                total_score_deductions += 10
            elif rep["min_knee_angle"] < 70:
                rep_errors.append("Extreme knee flexion. Avoid dropping too fast or too deep to protect the joint.")
                total_score_deductions += 5
                
            # Check 2: Torso Posture Forward Lean Check
            if rep["max_torso_lean"] > 15:
                rep_errors.append("Forward torso lean detected. Keep your chest proud and stack your shoulders over your hips.")
                total_score_deductions += 15
                
            # Check 3: Alignment Over Toe Check
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
        
        # Summary Analytics output structural blueprint
        return {
            "summary": {
                "total_reps_counted": len(reps),
                "overall_form_score": form_score,
                "primary_improvement_target": self.get_primary_target(feedback_log)
            },
            "detailed_breakdown": feedback_log
        }

    def get_primary_target(self, feedback_log):
        """Helper to find the most frequent form breakdown across the set."""
        all_cues = [cue for rep in feedback_log for cue in rep["coaching_cues"]]
        if not all_cues or "Flawless form execution!" in all_cues:
            return "Maintain current consistency. Ready to increase volume or load."
        return max(set(all_cues), key=all_cues.count)

# Execution test harness code block
if __name__ == "__main__":
    analyzer = LungeAnalyzer()
    # Replace with your actual sandbox upload file test path
    analysis_output = analyzer.process_video("uploaded_workout_sample.mp4")
    print(json.dumps(analysis_output, indent=4))