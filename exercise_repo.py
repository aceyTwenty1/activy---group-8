# exercise_repo.py

EXERCISE_DATABASE = {
    "lunge": {
        "type": "dynamic",
        "tracking_joints": {"shoulder": 11, "hip": 23, "knee": 25, "ankle": 27, "toe": 31},
        "baseline_joint": "hip",
        "movement_direction": "descending",
        "threshold": 0.04,
        "checks": {
            "depth": {"type": "min_angle", "joint": "knee", "limit": 110, "fail_cue": "Low depth. Drop your hips lower until your thigh is parallel to the ground.", "penalty": 10},
            "over_flexion": {"type": "min_angle", "joint": "knee", "limit": 70, "fail_cue": "Extreme knee flexion. Avoid dropping too deep to protect the joint.", "penalty": 5},
            "lean": {"type": "max_angle", "joint": "torso", "limit": 15, "fail_cue": "Forward torso lean detected. Keep your chest proud and stack shoulders over hips.", "penalty": 15}
        }
    },
    "squat": {
        "type": "dynamic",
        "tracking_joints": {"hip": 23, "knee": 25, "ankle": 27},
        "baseline_joint": "hip",
        "movement_direction": "descending",
        "threshold": 0.05,
        "checks": {
            "depth": {"type": "min_angle", "joint": "knee", "limit": 100, "fail_cue": "Shallow squat. Try to drop your hips lower until thighs are parallel to the floor.", "penalty": 15}
        }
    },
    "push_up": {
        "type": "dynamic",
        "tracking_joints": {"shoulder": 11, "elbow": 13, "wrist": 15, "hip": 23, "ankle": 27},
        "baseline_joint": "shoulder",
        "movement_direction": "descending",
        "threshold": 0.05,
        "checks": {
            "depth": {"type": "min_angle", "joint": "elbow", "limit": 95, "fail_cue": "Incomplete depth. Bring your chest closer to the floor.", "penalty": 15},
            "sagging_core": {"type": "min_angle", "joint": "hip", "limit": 165, "fail_cue": "Sagging core! Keep your hips aligned straight with your shoulders.", "penalty": 20}
        }
    },
    "bicep_curl": {
        "type": "dynamic",
        "tracking_joints": {"shoulder": 11, "elbow": 13, "wrist": 15},
        "baseline_joint": "wrist",
        "movement_direction": "ascending",
        "threshold": 0.05,
        "checks": {
            "top_squeeze": {"type": "min_angle", "joint": "elbow", "limit": 60, "fail_cue": "Finish the rep! Squeeze your bicep completely at the top.", "penalty": 10}
        }
    },
    "glute_bridge": {
        "type": "dynamic",
        "tracking_joints": {"shoulder": 11, "hip": 23, "knee": 25},
        "baseline_joint": "hip",
        "movement_direction": "ascending",
        "threshold": 0.05,
        "checks": {
            "hyperextension": {"type": "max_angle", "joint": "hip", "limit": 185, "fail_cue": "Hips raised too high! Stop when your body forms a straight diagonal line.", "penalty": 10}
        }
    },
    "overhead_press": {
        "type": "dynamic",
        "tracking_joints": {"shoulder": 11, "elbow": 13, "wrist": 15},
        "baseline_joint": "wrist",
        "movement_direction": "ascending",
        "threshold": 0.06,
        "checks": {
            "lockout": {"type": "max_angle", "joint": "elbow", "limit": 160, "fail_cue": "Incomplete extension. Push up until your arms are fully extended.", "penalty": 10}
        }
    },
    "calf_raise": {
        "type": "dynamic",
        "tracking_joints": {"knee": 25, "ankle": 27, "toe": 31},
        "baseline_joint": "ankle",
        "movement_direction": "ascending",
        "threshold": 0.02,
        "checks": {
            "short_range": {"type": "min_angle", "joint": "ankle", "limit": 115, "fail_cue": "Push higher up on your toes for maximum calf engagement.", "penalty": 10}
        }
    },
    "lateral_raise": {
        "type": "dynamic",
        "tracking_joints": {"hip": 23, "shoulder": 11, "elbow": 13},
        "baseline_joint": "elbow",
        "movement_direction": "ascending",
        "threshold": 0.05,
        "checks": {
            "over_raising": {"type": "max_angle", "joint": "shoulder", "limit": 95, "fail_cue": "Arms raised too high. Stop when your hands align with your shoulders.", "penalty": 15}
        }
    },
    "plank": {
        "type": "static",
        "tracking_joints": {"shoulder": 11, "hip": 23, "ankle": 27},
        "checks": {
            "form_collapse": {"type": "angle_range", "joint": "hip", "min": 165, "max": 195, "fail_cue": "Keep your body in a straight line! Do not sag or pike your hips up.", "penalty": 20}
        }
    },
    "crunch": {
        "type": "dynamic",
        "tracking_joints": {"shoulder": 11, "hip": 23},
        "baseline_joint": "shoulder",
        "movement_direction": "descending",  # Shoulder moves down relative to frame orientation
        "threshold": 0.03,
        "checks": {
            "short_range": {"type": "max_angle", "joint": "hip", "limit": 45, "fail_cue": "Contract harder. Elevate your shoulders fully off the mat.", "penalty": 10}
        }
    }
}

def get_exercise_profile(name):
    """Safely retrieves rules mapping configurations."""
    return EXERCISE_DATABASE.get(name.lower(), None)