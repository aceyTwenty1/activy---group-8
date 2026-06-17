# questionnaire.py
import json

def get_choice(prompt, options):
    """Prompts user for a choice from a list and validates the input."""
    while True:
        print(f"\nOptions: {', '.join(options)}")
        value = input(prompt).strip().lower()
        if value in options:
            return value
        print(f"[!] Invalid selection. Please choose from: {', '.join(options)}")

def get_numeric(prompt, min_val, max_val, is_float=False):
    """Prompts user for a number within a specific range and validates it."""
    while True:
        try:
            value = float(input(prompt)) if is_float else int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"[!] Out of bounds. Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("[!] Invalid input. Please enter a valid number.")

def run_fitness_intake():
    print("=" * 60)
    print("📋  ACTÍVY HEALTH & OBJECTIVE INTAKE SYSTEM")
    print("=" * 60)

    # 1. Biometrics
    print("\n[PART 1: BIOMETRICS]")
    age = get_numeric("Enter your age (10 - 100): ", 10, 100)
    gender = get_choice("Select gender: ", ["male", "female", "other"])
    weight = get_numeric("Enter current weight in kg (30 - 250): ", 30.0, 250.0, is_float=True)
    height = get_numeric("Enter current height in cm (100 - 250): ", 100.0, 250.0, is_float=True)

    # 2. Activity & Lifestyle
    print("\n[PART 2: ACTIVITY PROFILE]")
    activity = get_choice(
        "Select your current weekly activity level: ", 
        ["sedentary", "lightly active", "moderately active", "very active"]
    )

    # 3. Targets & Objectives
    print("\n[PART 3: TARGET GOALS]")
    goal = get_choice(
        "What is your primary fitness objective? ", 
        ["hypertrophy", "strength", "endurance", "fat loss"]
    )
    days = get_numeric("How many days per week can you dedicate to training? (2 - 6): ", 2, 6)

    # 4. Physical Constraints & Injuries
    print("\n[PART 4: SAFETY & PHYSICAL CONSTRAINTS]")
    has_injury = input("Do you currently experience joint pain or active injuries? (yes/no): ").strip().lower()
    
    injuries = []
    if has_injury in ["yes", "y"]:
        print("\nIdentify pain locations below (type 'done' to finish adding tracking flags):")
        available_joints = ["knee", "shoulder", "elbow", "hip", "ankle", "back"]
        while True:
            print(f"Tracked locations: {', '.join(available_joints)}")
            inj = input("Enter injury location or 'done': ").strip().lower()
            if inj == "done":
                break
            if inj in available_joints:
                if inj not in injuries:
                    injuries.append(inj)
                    print(f"[+] Flagged {inj} tracking safety restrictions.")
                else:
                    print("[-] Location already added to restrictions log.")
            else:
                print("[!] Joint focus not tracked in system schema rules.")

    # Bundle the profile data
    user_profile = {
        "biometrics": {
            "age": age,
            "gender": gender,
            "weight_kg": weight,
            "height_cm": height
        },
        "lifestyle": {
            "activity_tier": activity
        },
        "objectives": {
            "primary_goal": goal,
            "days_per_week": days
        },
        "safety_constraints": {
            "flagged_injuries": injuries if injuries else ["none"]
        }
    }

    # Save to a local JSON file so other scripts can access it
    with open("user_profile.json", "w") as f:
        json.dump(user_profile, f, indent=4)

    print("\n" + "=" * 60)
    print("[✓] Profile compiled successfully! Saved to 'user_profile.json'.")
    print("=" * 60)
    print(json.dumps(user_profile, indent=4))

if __name__ == "__main__":
    run_fitness_intake()