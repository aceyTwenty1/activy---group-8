import customtkinter as ctk
class TabTournaments(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="🏆 Tournament Discovery & Passport Feeds", font=("Arial", 18, "bold")).pack(pady=20)
