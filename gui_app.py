# gui_app.py
import tkinter as tk
from tkinter import ttk, messagebox
import json

class ActivyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ ACTÍVY — Group 8")
        self.root.geometry("800x900")
        self.root.configure(bg="#0B0B0E")

        # Set up modern dark-mode styles
        self.setup_styles()
        
        # Main layout frame container
        self.main_container = ttk.Frame(root, style="Main.TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Title Block Banner
        title_label = tk.Label(
            self.main_container, 
            text="⚡ ACTÍVY ENGINE INTELLIGENCE", 
            font=("Segoe UI", 20, "bold"), 
            fg="#00FF66", 
            bg="#0B0B0E"
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        subtitle_label = tk.Label(
            self.main_container, 
            text="Predictive physiological modeling and mechanical constraint filtering.", 
            font=("Segoe UI", 10), 
            fg="#8A8A93", 
            bg="#0B0B0E"
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, 25))

        # --- PANEL 1: BIOMETRICS FORM MATRIX ---
        bio_frame = ttk.LabelFrame(self.main_container, text=" BIOMETRIC METRICS ", style="Card.TLabelframe")
        bio_frame.pack(fill=tk.X, pady=12)
        
        # Grid fields
        tk.Label(bio_frame, text="Age (yrs)", font=("Segoe UI", 9, "bold"), fg="#8A8A93", bg="#16161A").grid(row=0, column=0, padx=15, pady=10, sticky=tk.W)
        self.age_spin = ttk.Spinbox(bio_frame, from_=10, to=100, width=10, style="Custom.TSpinbox")
        self.age_spin.set(20)
        self.age_spin.grid(row=1, column=0, padx=15, pady=(0, 15), sticky=tk.W)

        tk.Label(bio_frame, text="Gender Profile", font=("Segoe UI", 9, "bold"), fg="#8A8A93", bg="#16161A").grid(row=0, column=1, padx=15, pady=10, sticky=tk.W)
        self.gender_combo = ttk.Combobox(bio_frame, values=["Male", "Female", "Other"], width=14, state="readonly", style="Custom.TCombobox")
        self.gender_combo.set("Male")
        self.gender_combo.grid(row=1, column=1, padx=15, pady=(0, 15), sticky=tk.W)

        tk.Label(bio_frame, text="Weight (kg)", font=("Segoe UI", 9, "bold"), fg="#8A8A93", bg="#16161A").grid(row=0, column=2, padx=15, pady=10, sticky=tk.W)
        self.weight_entry = ttk.Entry(bio_frame, width=12, style="Custom.TEntry")
        self.weight_entry.insert(0, "70")
        self.weight_entry.grid(row=1, column=2, padx=15, pady=(0, 15), sticky=tk.W)

        tk.Label(bio_frame, text="Height (cm)", font=("Segoe UI", 9, "bold"), fg="#8A8A93", bg="#16161A").grid(row=0, column=3, padx=15, pady=10, sticky=tk.W)
        self.height_entry = ttk.Entry(bio_frame, width=12, style="Custom.TEntry")
        self.height_entry.insert(0, "175")
        self.height_entry.grid(row=1, column=3, padx=15, pady=(0, 15), sticky=tk.W)

        # --- PANEL 2: STRATEGIC TARGET CONFIGURATIONS ---
        target_frame = ttk.LabelFrame(self.main_container, text=" PERFORMANCE GOALS & PARAMETERS ", style="Card.TLabelframe")
        target_frame.pack(fill=tk.X, pady=12)

        tk.Label(target_frame, text="Current Activity Tier", font=("Segoe UI", 9, "bold"), fg="#8A8A93", bg="#16161A").grid(row=0, column=0, padx=15, pady=10, sticky=tk.W)
        self.activity_combo = ttk.Combobox(target_frame, values=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"], width=22, state="readonly", style="Custom.TCombobox")
        self.activity_combo.set("Moderately Active")
        self.activity_combo.grid(row=1, column=0, padx=15, pady=(0, 15), sticky=tk.W)

        tk.Label(target_frame, text="Primary Fitness Objective", font=("Segoe UI", 9, "bold"), fg="#8A8A93", bg="#16161A").grid(row=0, column=1, padx=15, pady=10, sticky=tk.W)
        self.goal_combo = ttk.Combobox(target_frame, values=["Hypertrophy", "Strength", "Endurance", "Fat Loss"], width=22, state="readonly", style="Custom.TCombobox")
        self.goal_combo.set("Strength")
        self.goal_combo.grid(row=1, column=1, padx=15, pady=(0, 15), sticky=tk.W)

        tk.Label(target_frame, text="Weekly Target Frequency (Days)", font=("Segoe UI", 9, "bold"), fg="#8A8A93", bg="#16161A").grid(row=0, column=2, padx=15, pady=10, sticky=tk.W)
        self.days_slider = tk.Scale(target_frame, from_=2, to=6, orient=tk.HORIZONTAL, bg="#16161A", fg="#00FF66", font=("Segoe UI", 9, "bold"), highlightthickness=0, troughcolor="#26262B", activebackground="#00FF66", length=180)
        self.days_slider.set(4)
        self.days_slider.grid(row=1, column=2, padx=15, pady=(0, 15), sticky=tk.W)

        # --- PANEL 3: SAFETY MECHANICAL FILTERS ---
        injury_frame = ttk.LabelFrame(self.main_container, text=" ISOLATION LOCKS (JOINT INJURY SAFETY LAYER) ", style="Card.TLabelframe")
        injury_frame.pack(fill=tk.X, pady=12)

        self.injury_vars = {}
        joints = ["Knee", "Shoulder", "Elbow", "Hip", "Ankle", "Back"]
        for idx, joint in enumerate(joints):
            var = tk.BooleanVar(value=False)
            self.injury_vars[joint.lower()] = var
            cb = tk.Checkbutton(
                injury_frame, 
                text=joint, 
                variable=var, 
                bg="#16161A", 
                fg="#E4E4E7", 
                selectcolor="#26262B", 
                activebackground="#16161A", 
                activeforeground="#00FF66",
                font=("Segoe UI", 10)
            )
            cb.grid(row=0, column=idx, padx=16, pady=15, sticky=tk.W)

        # --- ACTION RUN RUNNER ACTION TRIGGER ---
        self.btn_generate = tk.Button(
            self.main_container, 
            text="⚡ GENERATE BIOMECHANICAL WORKOUT BLUEPRINT", 
            font=("Segoe UI", 11, "bold"), 
            bg="#00FF66", 
            fg="#0B0B0E", 
            activebackground="#00D957", 
            activeforeground="#0B0B0E",
            bd=0, 
            cursor="hand2",
            pady=12,
            command=self.process_and_display_plan
        )
        self.btn_generate.pack(fill=tk.X, pady=20)

        # --- PANEL 4: ANALYTICS RUN ENGINE OUTPUT ---
        output_frame = ttk.LabelFrame(self.main_container, text=" COMPILED EXECUTION PROTOCOL ", style="Card.TLabelframe")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.txt_output = tk.Text(
            output_frame, 
            bg="#0D0D11", 
            fg="#00FF66", 
            insertbackground="white", 
            font=("Consolas", 10), 
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#26262B",
            highlightcolor="#00FF66",
            padx=10,
            pady=10
        )
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.txt_output.insert(tk.END, "// System tracking execution stream idle. Initialize compilation map tracking profile details...")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Main.TFrame", background="#0B0B0E")
        
        # Style layout mapping frames
        style.configure("Card.TLabelframe", background="#16161A", bordercolor="#26262B", borderwidth=1)
        style.configure("Card.TLabelframe.Label", background="#0B0B0E", foreground="#8A8A93", font=("Segoe UI", 8, "bold"))
        
        # Interactive forms styling options variables configurations
        style.configure("Custom.TEntry", fieldbackground="#26262B", foreground="#E4E4E7", bordercolor="#3F3F46", lightcolor="#26262B", darkcolor="#26262B", insertcolor="white")
        style.configure("Custom.TCombobox", fieldbackground="#26262B", foreground="#E4E4E7", background="#3F3F46", bordercolor="#3F3F46", arrowcolor="#00FF66")
        style.map("Custom.TCombobox", fieldbackground=[("readonly", "#26262B")], foreground=[("readonly", "#E4E4E7")])
        
        style.configure("Custom.TSpinbox", fieldbackground="#26262B", foreground="#E4E4E7", background="#26262B", bordercolor="#3F3F46", arrowcolor="#00FF66")

    def process_and_display_plan(self):
        try:
            age = int(self.age_spin.get())
            gender = self.gender_combo.get().lower()
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            activity = self.activity_combo.get().lower()
            goal = self.goal_combo.get().lower()
            days = self.days_slider.get()

            flagged_injuries = [joint for joint, var in self.injury_vars.items() if var.get()]

            height_m = height / 100.0
            bmi = round(weight / (height_m ** 2), 1)

            if gender == "male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

            multipliers = {"sedentary": 1.2, "lightly active": 1.375, "moderately active": 1.55, "very active": 1.725}
            tdee = round(bmr * multipliers.get(activity, 1.2))

            if days <= 3:
                split_name = "Full Body System Split"
                days_list = ["Day 1: Full Body Workout", "Day 2: Recovery Phase", "Day 3: Full Body Workout", "Day 4: Recovery Phase", "Day 5: Full Body Workout"]
            elif days == 4:
                split_name = "Upper Body / Lower Body Split"
                days_list = ["Day 1: Upper Body Focus", "Day 2: Lower Body Focus", "Day 3: Recovery Phase", "Day 4: Upper Body Focus", "Day 5: Lower Body Focus"]
            else:
                split_name = "Push / Pull / Legs Structural Split"
                days_list = ["Day 1: Push Routine", "Day 2: Pull Routine", "Day 3: Leg Extension Mechanics", "Day 4: Recovery Phase", "Day 5: Cycle Reset"]

            all_exercises = ["Squat", "Push-Up", "Lunge", "Bicep Curl", "Plank", "Glute Bridge", "Overhead Press", "Calf Raise", "Lateral Raise", "Crunch"]
            safe_pool = []
            
            for ex in all_exercises:
                ex_l = ex.lower()
                if "knee" in flagged_injuries and ex_l in ["squat", "lunge"]: continue
                if "shoulder" in flagged_injuries and ex_l in ["push-up", "overhead_press", "lateral_raise"]: continue
                if "elbow" in flagged_injuries and ex_l in ["push-up", "bicep_curl", "overhead_press"]: continue
                if "back" in flagged_injuries and ex_l in ["squat", "lunge", "crunch"]: continue
                safe_pool.append(ex)

            profile_data = {
                "biometric_assessment": {
                    "calculated_bmi": bmi,
                    "basal_metabolic_rate_kcal": round(bmr),
                    "total_daily_energy_expenditure_kcal": tdee
                },
                "workout_blueprint": {
                    "recommended_split_type": split_name,
                    "frequency_target": f"{days} Days per week",
                    "weekly_schedule_layout": days_list[:days],
                    "approved_exercise_pool": safe_pool,
                    "active_safety_restrictions": flagged_injuries if flagged_injuries else ["None Detected"]
                }
            }

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, json.dumps(profile_data, indent=4))

        except ValueError:
            messagebox.showerror("Configuration Error", "Please verify numeric entries for weight and height values are accurate.")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = ActivyGUI(app_root)
    app_root.mainloop()