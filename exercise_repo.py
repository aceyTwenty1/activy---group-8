# ==============================================================================
# exercise_repo.py
# ==============================================================================

# This dictionary holds all movement configurations, angle thresholds, and cues.
EXERCISE_REPOSITORY = {
    "push_up": {
        "name": "Standard Push-Up",
        "plane": "horizontal",  # Torso angle target must be flat (< 45 degrees)
        "tracking_landmarks": {
            "primary": ["shoulder", "elbow", "wrist"]
        },
        "thresholds": {
            "target_elbow_flexion": 90,
            "min_depth_y": 0.40
        },
        "coaching_cues": [
            "Drop deeper! Your elbows haven't reached 90 degrees yet.",
            "Keep your core locked and hips level."
        ]
    },
    "plank": {
        "name": "Forearm Plank",
        "plane": "horizontal",
        "tracking_landmarks": {
            "primary": ["shoulder", "hip", "ankle"]
        },
        "thresholds": {
            "max_hip_sag_angle": 160,
            "min_hip_sag_angle": 200
        },
        "coaching_cues": [
            "Don't let your hips sag toward the floor!",
            "Keep your body in a straight line."
        ]
    },
    "squat": {
        "name": "Bodyweight Squat",
        "plane": "vertical",  # Torso angle target must be upright (> 45 degrees)
        "tracking_landmarks": {
            "primary": ["hip", "knee", "ankle"]
        },
        "thresholds": {
            "target_depth_angle": 95,
            "min_depth_y": 0.52
        },
        "coaching_cues": [
            "Squat lower! Try to bring your thighs parallel to the ground.",
            "Keep your chest proud and drive through your heels."
        ]
    },
    "deadlift": {
        "name": "Conventional Deadlift",
        "plane": "vertical",
        "tracking_landmarks": {
            "primary": ["shoulder", "hip", "knee"]
        },
        "thresholds": {
            "max_back_rounding_angle": 150
        },
        "coaching_cues": [
            "Flatten your spine! Flatten your back to protect your lumbar.",
            "Drive hard through your legs."
        ]
    }
}

# The block below handles standalone validation checks smoothly without circular loops
if __name__ == "__main__":
    print("[✓] Exercise Repository blueprint successfully initialized.")
    print("-" * 50)
    for key, data in EXERCISE_REPOSITORY.items():
        print(f" -> Key: '{key}' mapped to profile: [{data['name']}] ({data['plane'].upper()} plane)")