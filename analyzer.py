import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import urllib.request
from collections import Counter
from exercise_repo import EXERCISE_REPOSITORY

class VisualExerciseAnalyzer:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(dir_path, 'pose_landmarker_full.task')
        
        if not os.path.exists(model_path):
            print("[⚙️] Downloading 'pose_landmarker_full.task' bundle...")
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task"
            urllib.request.urlretrieve(url, model_path)

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(base_options=base_options, output_segmentation_masks=False)
        self.detector = vision.PoseLandmarker.create_from_options(options)

        self.MEDIAPIPE_LANDMARK_MAP = {
            "nose": 0, "ear": 8,
            "left_shoulder": 11, "right_shoulder": 12,
            "left_elbow": 13, "right_elbow": 14,
            "left_wrist": 15, "right_wrist": 16,
            "left_hip": 23, "right_hip": 24,
            "left_knee": 25, "right_knee": 26,
            "left_ankle": 27, "right_ankle": 28,
            "left_foot": 31, "right_foot": 32
        }
        
        self.smoothed_world_points = {}
        self.smoothed_draw_points = {}
        self.alpha = 0.08

    def calculate_3d_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        ba_norm = ba / np.linalg.norm(ba)
        bc_norm = bc / np.linalg.norm(bc)
        dot_product = np.dot(ba_norm, bc_norm)
        angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
        return round(np.degrees(angle), 2)

    def apply_ema_filter(self, joint_key, current_coord):
        if joint_key not in self.smoothed_world_points:
            self.smoothed_world_points[joint_key] = current_coord
        else:
            prev = np.array(self.smoothed_world_points[joint_key])
            curr = np.array(current_coord)
            smoothed = self.alpha * curr + (1 - self.alpha) * prev
            self.smoothed_world_points[joint_key] = tuple(smoothed)
        return self.smoothed_world_points[joint_key]

    def scan_frame_for_exercise(self, draw_points, world_points):
        """Identifies active profile using angle thresholds on the most visible side."""
        side = None
        if "left_shoulder" in draw_points and "left_hip" in draw_points:
            side = "left"
        elif "right_shoulder" in draw_points and "right_hip" in draw_points:
            side = "right"
            
        if not side:
            return None

        sh = draw_points[f"{side}_shoulder"]
        hip = draw_points[f"{side}_hip"]
        torso_angle = np.abs(np.degrees(np.arctan2(hip[1] - sh[1], hip[0] - sh[0])))
        if torso_angle > 90:
            torso_angle = 180 - torso_angle

        # --- HORIZONTAL PLANE ANALYSIS ---
        if torso_angle < 45:
            if f"{side}_shoulder" in world_points and f"{side}_elbow" in world_points and f"{side}_wrist" in world_points:
                elbow_angle = self.calculate_3d_angle(
                    world_points[f"{side}_shoulder"], 
                    world_points[f"{side}_elbow"], 
                    world_points[f"{side}_wrist"]
                )
                
                if 60 < elbow_angle < 115:
                    return "low_plank"
                elif elbow_angle >= 150:
                    return "high_plank"
                
            return "push_up"

        # --- VERTICAL PLANE ANALYSIS ---
        else:
            if f"{side}_hip" in world_points and f"{side}_knee" in world_points:
                return "squat"
            return "dumbell_bicep_curl"

    def draw_skeleton(self, target_frame, points, color, thickness=4):
        for side in ["left", "right"]:
            if f"{side}_hip" in points and f"{side}_knee" in points:
                cv2.line(target_frame, points[f"{side}_hip"], points[f"{side}_knee"], color, thickness)
            if f"{side}_knee" in points and f"{side}_ankle" in points:
                cv2.line(target_frame, points[f"{side}_knee"], points[f"{side}_ankle"], color, thickness)
        
        if "left_shoulder" in points and "left_hip" in points:
            cv2.line(target_frame, points["left_shoulder"], points["left_hip"], color, thickness)
        if "right_shoulder" in points and "right_hip" in points:
            cv2.line(target_frame, points["right_shoulder"], points["right_hip"], color, thickness)
        if "left_shoulder" in points and "right_shoulder" in points:
            cv2.line(target_frame, points["left_shoulder"], points["right_shoulder"], color, thickness)
        if "left_hip" in points and "right_hip" in points:
            cv2.line(target_frame, points["left_hip"], points["right_hip"], color, thickness)

        for side in ["left", "right"]:
            if f"{side}_shoulder" in points and f"{side}_elbow" in points:
                cv2.line(target_frame, points[f"{side}_shoulder"], points[f"{side}_elbow"], color, thickness)
            if f"{side}_elbow" in points and f"{side}_wrist" in points:
                cv2.line(target_frame, points[f"{side}_elbow"], points[f"{side}_wrist"], color, thickness)

        for joint_name, coord in points.items():
            cv2.circle(target_frame, coord, thickness + 1, (255, 255, 255), -1)

    def process_and_draw_video(self, video_path, output_path):
        self.smoothed_world_points.clear()
        self.smoothed_draw_points.clear()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[!] Error: Could not load video path: {video_path}")
            return

        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # ==========================================
        # PASS 1: INTELLIGENT DEEP SCAN
        # ==========================================
        print("[⚙️] PASS 1: Scanning core workout frames...")
        start_scan_frame = min(45, max(0, total_frames - 70))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_scan_frame)
        
        detection_buffer = []
        scan_count = 0

        while cap.isOpened() and scan_count < 50:
            ret, frame = cap.read()
            if not ret:
                break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.detector.detect(mp_image)
            
            if detection_result.pose_landmarks:
                landmarks = detection_result.pose_landmarks[0]
                draw_points = {}
                world_points = {}
                
                for joint_key, idx in self.MEDIAPIPE_LANDMARK_MAP.items():
                    if idx < len(landmarks):
                        lm = landmarks[idx]
                        draw_points[joint_key] = (int(lm.x * width), int(lm.y * height))
                        world_points[joint_key] = (lm.x, lm.y, lm.z)
                
                detected_id = self.scan_frame_for_exercise(draw_points, world_points)
                if detected_id:
                    detection_buffer.append(detected_id)
            scan_count += 1

        if detection_buffer:
            exercise_name, count = Counter(detection_buffer).most_common(1)[0]
            profile = EXERCISE_REPOSITORY[exercise_name]
            print(f"[✓] Definitive Target Locked: {profile.get('name')}")
        else:
            print("[!] Identification buffer empty. Defaulting to standard profile.")
            exercise_name = "push_up"
            profile = EXERCISE_REPOSITORY[exercise_name]

        # ==========================================
        # PASS 2: CLEAN STABILIZED RENDER
        # ==========================================
        print("[⚙️] PASS 2: Generating smooth visual framework overlay...")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.detector.detect(mp_image)
            
            if detection_result.pose_landmarks:
                landmarks = detection_result.pose_landmarks[0]
                draw_points = {}
                world_points = {}
                visibilities = {}
                
                for joint_key, idx in self.MEDIAPIPE_LANDMARK_MAP.items():
                    if idx < len(landmarks):
                        lm = landmarks[idx]
                        raw_draw = (int(lm.x * width), int(lm.y * height))
                        raw_world = (lm.x, lm.y, lm.z)
                        
                        world_points[joint_key] = self.apply_ema_filter(joint_key, raw_world)
                        visibilities[joint_key] = lm.visibility
                        
                        if joint_key not in self.smoothed_draw_points:
                            self.smoothed_draw_points[joint_key] = raw_draw
                        else:
                            prev_d = np.array(self.smoothed_draw_points[joint_key])
                            curr_d = np.array(raw_draw)
                            smoothed_d = self.alpha * curr_d + (1 - self.alpha) * prev_d
                            self.smoothed_draw_points[joint_key] = (int(smoothed_d[0]), int(smoothed_d[1]))
                        
                        draw_points[joint_key] = self.smoothed_draw_points[joint_key]

                if profile is not None:
                    thresholds = profile.get("thresholds", {})
                    cues = profile.get("coaching_cues", ["Form stable"])
                    
                    rig_color = (0, 255, 0)
                    status_text = f"{profile.get('name').upper()}: STABLE"
                    show_ghost = False
                    ghost_draw_points = draw_points.copy()

                    # --- VERTICAL MATRIX ---
                    if profile.get("plane") == "vertical":
                        left_vis = visibilities.get("left_knee", 0)
                        right_vis = visibilities.get("right_knee", 0)
                        side = "left" if left_vis >= right_vis else "right"

                        if f"{side}_hip" in world_points and f"{side}_knee" in world_points and f"{side}_ankle" in world_points:
                            knee_angle = self.calculate_3d_angle(world_points[f"{side}_hip"], world_points[f"{side}_knee"], world_points[f"{side}_ankle"])
                            if "squat" in exercise_name:
                                if draw_points[f"{side}_hip"][1] > (height * thresholds.get("min_depth_y", 0.52)):
                                    if knee_angle > thresholds.get("target_depth_angle", 90):
                                        rig_color = (0, 0, 255)
                                        status_text = f"WARNING: {cues[0]}"
                                        show_ghost = True
                                        hip_x, hip_y = ghost_draw_points[f"{side}_hip"]
                                        ankle_y = ghost_draw_points[f"{side}_ankle"][1]
                                        ghost_draw_points[f"{side}_hip"] = (hip_x, int(ankle_y - (ankle_y - hip_y) * 1.15))

                    # --- HORIZONTAL MATRIX ---
                    elif profile.get("plane") == "horizontal":
                        left_valid, right_valid = False, False
                        left_angle, right_angle = 0, 0

                        if "left_shoulder" in world_points and "left_elbow" in world_points and "left_wrist" in world_points:
                            left_angle = self.calculate_3d_angle(world_points["left_shoulder"], world_points["left_elbow"], world_points["left_wrist"])
                            left_valid = True

                        if "right_shoulder" in world_points and "right_elbow" in world_points and "right_wrist" in world_points:
                            right_angle = self.calculate_3d_angle(world_points["right_shoulder"], world_points["right_elbow"], world_points["right_wrist"])
                            right_valid = True

                        side, elbow_angle = None, None
                        if left_valid and right_valid:
                            side, elbow_angle = ("left", left_angle) if visibilities.get("left_elbow", 0) >= visibilities.get("right_elbow", 0) else ("right", right_angle)
                        elif left_valid:
                            side, elbow_angle = "left", left_angle
                        elif right_valid:
                            side, elbow_angle = "right", right_angle

                        if side is not None and "push_up" in exercise_name:
                            if draw_points[f"{side}_shoulder"][1] > (height * thresholds.get("min_depth_y", 0.40)):
                                if elbow_angle > thresholds.get("target_elbow_flexion", 90):
                                    rig_color = (0, 0, 255)
                                    status_text = f"WARNING: {cues[0]}"
                                    show_ghost = True
                                    sh_x, sh_y = ghost_draw_points[f"{side}_shoulder"]
                                    wr_x, wr_y = ghost_draw_points[f"{side}_wrist"]
                                    ghost_draw_points[f"{side}_elbow"] = (int((sh_x + wr_x) / 2) - 25, int((sh_y + wr_y) / 2) + 15)

                        elif side is not None and "high_plank" in exercise_name:
                            ideal_locked_angle = 180.0
                            angle_deviation = abs(ideal_locked_angle - elbow_angle)
                            if angle_deviation > thresholds.get("max_arm_drift_deviation", 30):
                                rig_color = (0, 0, 255)
                                status_text = f"WARNING: {cues[0]}"

                    self.draw_skeleton(frame, draw_points, rig_color, thickness=4)

                    if show_ghost:
                        ghost_overlay = frame.copy()
                        self.draw_skeleton(ghost_overlay, ghost_draw_points, (255, 255, 0), thickness=5)
                        frame = cv2.addWeighted(ghost_overlay, 0.35, frame, 0.65, 0)

                    cv2.putText(frame, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, rig_color, 2)
            
            out.write(frame)

        cap.release()
        out.release()
        print(f"[✓] Analysis successfully outputted to: {output_path}")