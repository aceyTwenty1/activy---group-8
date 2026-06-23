import customtkinter as ctk
class TabAcademy(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="🏢 Academy & Team Management Hub", font=("Arial", 18, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text="Roster Active Count: 0 Athletes linked via B2B Key").pack(pady=10)
