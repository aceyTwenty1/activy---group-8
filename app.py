import os
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Import your existing analyzer engine
from analyzer import VisualExerciseAnalyzer

# Set window themes
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ActivyGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize backend analyzer engine
        self.analyzer = VisualExerciseAnalyzer()
        self.selected_video_path = None

        # Window Configurations
        self.title("AKTIVY // Group 8 - Pose Analytics Engine")
        self.geometry("680x420")
        self.resizable(False, False)

        # ------------------ UI LAYOUT ------------------
        
        # Title Label
        self.title_label = ctk.CTkLabel(
            self, 
            text="AKTIVY // TRACKER", 
            font=ctk.CTkFont(family="Helvetica", size=26, weight="bold")
        )
        self.title_label.pack(pady=(30, 5))

        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Automated Computer Vision Fitness Analytics Engine", 
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 25))

        # Main Interaction Frame
        self.main_frame = ctk.CTkFrame(self, width=600, height=180, corner_radius=10)
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(pady=10)

        # Selected File Indicator Path
        self.file_label = ctk.CTkLabel(
            self.main_frame, 
            text="No video file selected. Tap browse to begin.", 
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="dark gray"
        )
        self.file_label.pack(pady=(35, 15), padx=20)

        # Button Group Layout Row
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(pady=5)

        self.browse_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Browse Video", 
            command=self.browse_video,
            width=140,
            height=35,
            font=ctk.CTkFont(weight="bold")
        )
        self.browse_btn.grid(row=0, column=0, padx=10)

        self.analyze_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Analyze Form", 
            command=self.start_analysis_thread,
            state="disabled",
            fg_color="#2c3e50",
            width=140,
            height=35,
            font=ctk.CTkFont(weight="bold")
        )
        self.analyze_btn.grid(row=0, column=1, padx=10)

        # Status Label / Feedback
        self.status_label = ctk.CTkLabel(
            self, 
            text="System Ready", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3498db"
        )
        self.status_label.pack(pady=(20, 0))

        # Mini Progress Indicator Bar
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

    def browse_video(self):
        """Opens native file window to select a specific video file cleanly."""
        file_types = [("Video Files", "*.mp4 *.avi *.mov *.mkv")]
        chosen_path = filedialog.askopenfilename(title="Select Workout Video Asset", filetypes=file_types)
        
        if chosen_path:
            self.selected_video_path = chosen_path
            filename = os.path.basename(chosen_path)
            
            # Display file name on the app layout interface
            self.file_label.configure(text=f"Selected File: {filename}", text_color="#1abc9c", font=ctk.CTkFont(slant="roman" \
            ""))
            
            # Activate processing buttons safely
            self.analyze_btn.configure(state="normal", fg_color="#2ecc71", hover_color="#27ae60")
            self.status_label.configure(text="Video Loaded. Click 'Analyze Form' to generate analytics.", text_color="#3498db")
            self.progress_bar.set(0)

    def start_analysis_thread(self):
        """Runs video processing in a background thread to keep the GUI responsive."""
        self.browse_btn.configure(state="disabled")
        self.analyze_btn.configure(state="disabled", fg_color="#2c3e50")
        self.status_label.configure(text="Processing video frameworks... Please wait.", text_color="#e67e22")
        self.progress_bar.configure(mode="indefinite")
        self.progress_bar.start()

        # Spin up background execution loop task
        threading.Thread(target=self.run_backend_analysis, daemon=True).start()

    def run_backend_analysis(self):
        try:
            input_dir = os.path.dirname(self.selected_video_path)
            input_filename = os.path.basename(self.selected_video_path)
            
            # Create a smart dynamic output name without mutating or needing user renames
            output_filename = f"analyzed_{input_filename}"
            output_path = os.path.join(input_dir, output_filename)

            # Route file paths straight to the engine layer
            self.analyzer.process_and_draw_video(self.selected_video_path, output_path)
            
            # Update GUI layout flags safely back on completion parameters
            self.after(0, lambda: self.on_analysis_complete(output_path))
        except Exception as e:
            self.after(0, lambda: self.on_analysis_failed(str(e)))

    def on_analysis_complete(self, output_path):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        
        self.browse_btn.configure(state="normal")
        self.status_label.configure(text="Analysis Finished Perfect!", text_color="#2ecc71")
        
        # Inform consumer precisely where data saved without file overlap issues
        filename = os.path.basename(output_path)
        self.file_label.configure(text=f"Saved asset inside current source directory as:\n{filename}", text_color="#2ecc71")

    def on_analysis_failed(self, error_msg):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        self.browse_btn.configure(state="normal")
        self.status_label.configure(text="An tracking error occurred.", text_color="#e74c3c")
        self.file_label.configure(text=f"Error Log trace detail: {error_msg}", text_color="#e74c3c")

if __name__ == "__main__":
    app = ActivyGUI()
    app.mainloop()