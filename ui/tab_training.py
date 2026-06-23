import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
# Import your backend processing engine
from analyzer import VisualExerciseAnalyzer

class TabTraining(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        self.db = db_handler
        self.analyzer = VisualExerciseAnalyzer()

        # Title
        ctk.CTkLabel(self, text="📋 Daily Training Logs", font=("Arial", 18, "bold")).pack(pady=15)
        
        # Checkboxes
        ctk.CTkCheckBox(self, text="Morning Strength Block (Complete)").pack(pady=10)
        ctk.CTkCheckBox(self, text="Technical Skill Session").pack(pady=10)
        
        # --- AI Pose Analysis Section ---
        self.status_label = ctk.CTkLabel(self, text="AI Form Coaching", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=(30, 5))

        self.upload_btn = ctk.CTkButton(
            self, 
            text="🎥 Upload Workout for AI Analysis", 
            command=self.start_video_analysis,
            fg_color="#1f538d",
            hover_color="#14375e"
        )
        self.upload_btn.pack(pady=10)

        self.progress_label = ctk.CTkLabel(self, text="", font=("Arial", 11, "italic"), text_color="gray")
        self.progress_label.pack(pady=5)

    def start_video_analysis(self):
        # Open file explorer to select a video file
        file_path = filedialog.askopenfilename(
            title="Select Workout Video",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )
        
        if not file_path:
            return  # User cancelled selection

        # Disable the button and show loading state
        self.upload_btn.configure(state="disabled", text="⚡ Processing Form...")
        self.progress_label.configure(text="Analyzing video frames with MediaPipe. Please wait...")

        # Run analysis in a separate thread so the CustomTkinter GUI stays responsive
        analysis_thread = threading.Thread(target=self.run_backend_analysis, args=(file_path,))
        analysis_thread.daemon = True
        analysis_thread.start()

    def run_backend_analysis(self, input_video_path):
        try:
            # Set up output path next to the script directory
            dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            output_video_path = os.path.join(dir_path, "output_analyzed_workout.mp4")

            # Fire up the backend analyzer engine!
            self.analyzer.process_and_draw_video(input_video_path, output_video_path)

            # Update GUI elements safely back on the main thread loop
            self.after(0, lambda: self.analysis_complete(success=True, path=output_video_path))
            
        except Exception as e:
            self.after(0, lambda: self.analysis_complete(success=False, error_msg=str(e)))

    def analysis_complete(self, success, path=None, error_msg=""):
        # Re-enable the interface controls
        self.upload_btn.configure(state="normal", text="🎥 Upload Workout for AI Analysis")
        
        if success:
            self.progress_label.configure(text=f"✓ Done! Output saved to: {os.path.basename(path)}")
            messagebox.showinfo("Analysis Complete", f"Workout analyzed successfully!\nSaved to: {path}")
        else:
            self.progress_label.configure(text="❌ Analysis failed.")
            messagebox.showerror("Error", f"An error occurred during video tracking:\n{error_msg}")