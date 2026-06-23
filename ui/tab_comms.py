import customtkinter as ctk
class TabComms(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="💬 Role-Based Communications (Sendbird/Stream SDK Gateway)", font=("Arial", 18, "bold")).pack(pady=20)
        ctk.CTkButton(self, text="Connect Athlete Channel", width=200).pack(pady=10)
        ctk.CTkButton(self, text="Connect Physio Channel", width=200).pack(pady=10)
