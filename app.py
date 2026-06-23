import customtkinter as ctk
from database.local_db import LocalDatabase
from ui.tab_passport import TabPassport
from ui.tab_comms import TabComms
from ui.tab_rehab import TabRehab
from ui.tab_training import TabTraining
from ui.tab_academy import TabAcademy
from ui.tab_tournaments import TabTournaments

class ActivyAppV1(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Activy Athlete System - V1 Enterprise")
        self.geometry("1100x650")
        self.db = LocalDatabase()

        self.tabview = ctk.CTkTabview(self, width=1050, height=600)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        tabs = {
            "Digital Passport": TabPassport,
            "Communications": TabComms,
            "Rehab Tracker": TabRehab,
            "Training Log": TabTraining,
            "Academy Manager": TabAcademy,
            "Tournaments": TabTournaments
        }
        
        for name, class_ref in tabs.items():
            self.tabview.add(name)
            frame = class_ref(self.tabview.tab(name), self.db)
            frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = ActivyAppV1()
    app.mainloop()
