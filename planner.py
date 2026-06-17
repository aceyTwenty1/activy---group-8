# planner.py
import json

class TrainingPlanner:
    def __init__(self):
        pass

    def calculate_metrics(self, age, weight, height, gender, activity_level):
        """Runs baseline physiological calculations."""
        # BMI Calculation
        height_m = height / 100.0
        bmi = round(weight / (height_m ** 2), 1)
        
        # BMR Calculation (Harris-Benedict Equation)
        if gender.lower() == "male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            
        # TDEE Activity Multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "lightly active": 1.375,
            "moderately active": 1.55,
            "very active": 1.725
        }
        multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
        tdee = round(bmr * multiplier)
        
        return {"bmi": bmi, "bmr": round(bmr), "tdee": tdee}

    def generate_routine(self, goal, days_per_week, injuries):
        """Selects optimal splits and applies safety filters for injuries."""
        # Determine routine distribution based on time availability
        if days_per_week <= 3:
            split_name = "Full Body Split"
            workout_days = ["Day 1: Full Body", "Day 2: Rest", "Day 3: Full Body", "Day 4: Rest", "Day 5: Full Body"]
        elif days_per_week == 4:
            split_name = "Upper / Lower Split"
            workout_days = ["Day 1: Upper Body", "Day 2: Lower Body", "Day 3: Rest", "Day 4: Upper Body", "Day 5: Lower Body"]
        else:
            split_name = "Push / Pull / Legs Split"
            workout_days = ["Day 1: Push (Chest/Triceps)", "Day 2: Pull (Back/Biceps)", "Day 3: Legs", "Day 4: Rest", "Day 5: Repeat"]

        # Base exercises mapping from your core repo
        exercises = ["Squat", "Push-Up", "Lunge", "Bicep Curl", "Plank", "Glute Bridge"]
        
        # Injury filtering safety layer
        filtered_exercises = []
        for ex in exercises:
            if "knee" in injuries.lower() and ex in ["Squat", "Lunge"]:
                continue # Skip knee-heavy joint exercises if injured
            if "shoulder" in injuries.lower() and ex in ["Push-Up", "Overhead Press"]:
                continue
            filtered_exercises.append(ex)

        return {
            "recommended_split": split_name,
            "weekly_schedule": workout_days[:days_per_week],
            "approved_exercise_pool": filtered_exercises,
            "coaching_rest_note": "Ensure 48 hours of recovery between tracking identical muscle targets."
        }

    def run_intake(self):
        """Interactive command line intake flow."""
        print("=" * 50)
        print("⚡ ACTÍVY PERSONALIZED INTAKE ENGINE ⚡")
        print("=" * 50)
        
        # Gather inputs
        age = int(input("Enter your age: "))
        gender = input("Enter gender (male/female): ").strip()
        weight = float(input("Enter weight in kg: "))
        height = float(input("Enter height in cm: "))
        
        print("\nActivity Levels: [sedentary, lightly active, moderately active, very active]")
        activity_level = input("Select your current activity tier: ").strip()
        
        print("\nGoals: [hypertrophy, strength, endurance, fat loss]")
        goal = input("Select your primary target objective: ").strip()
        
        days_per_week = int(input("How many days per week can you train? (2-6): "))
        injuries = input("List any joint pain/injuries (or type 'none'): ").strip()

        # Execute Engine Analytics Pass
        profile_metrics = self.calculate_metrics(age, weight, height, gender, activity_level)
        plan = self.generate_routine(goal, days_per_week, injuries)

        # Output Final Report Object
        report = {
            "user_metrics": profile_metrics,
            "training_profile": plan
        }
        
        print("\n" + "=" * 50)
        print("📊 GENERATED TRAINING ENGINE PROFILE SUMMARY")
        print("=" * 50)
        print(json.dumps(report, indent=4))

if __name__ == "__main__":
    engine = TrainingPlanner()
    engine.run_intake()