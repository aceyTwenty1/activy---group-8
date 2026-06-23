import customtkinter as ctk
import qrcode
from PIL import Image
import os

class TabPassport(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        self.db = db_handler
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.create_profile_form()
        self.create_digital_passport_card()

    def create_profile_form(self):
        form_frame = ctk.CTkFrame(self, corner_radius=12)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(form_frame, text="Athlete Profile Setup", font=("Arial", 20, "bold")).pack(pady=15)
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="Full Name", width=250)
        self.name_entry.pack(pady=10)
        self.sport_entry = ctk.CTkEntry(form_frame, placeholder_text="Sport (e.g., Football)", width=250)
        self.sport_entry.pack(pady=10)
        ctk.CTkButton(form_frame, text="Update Passport", command=self.save_and_refresh).pack(pady=20)

    def create_digital_passport_card(self):
        self.card_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1a1a1a")
        self.card_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(self.card_frame, text="Passport Matrix Offline", font=("Arial", 16)).pack(pady=40)

    def save_and_refresh(self):
        name, sport = self.name_entry.get(), self.sport_entry.get()
        os.makedirs("assets", exist_ok=True)
        qr = qrcode.make(f"Athlete: {name}\nSport: {sport}")
        qr.save("assets/temp_qr.png")
        for widget in self.card_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.card_frame, text=f"🌟 {name.upper()}", font=("Arial", 22, "bold"), text_color="#3a86ff").pack(pady=10)
        qr_img = ctk.CTkImage(Image.open("assets/temp_qr.png"), size=(150, 150))
        ctk.CTkLabel(self.card_frame, image=qr_img, text="").pack(pady=20)
