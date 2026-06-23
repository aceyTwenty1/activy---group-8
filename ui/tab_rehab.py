import customtkinter as ctk
class TabRehab(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="🏥 Injury & Rehabilitation Tracker", font=("Arial", 18, "bold")).pack(pady=20)
        self.log_box = ctk.CTkTextbox(self, width=400, height=150)
        self.log_box.pack(pady=10)
        self.log_box.insert("0.0", "Active Status: Clear / Fit to Train\nNo current restrictions logged by Physio.")
