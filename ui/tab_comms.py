import customtkinter as ctk
import threading
import traceback
from supabase import create_client, Client

# --- CLOUD CREDENTIALS ---
SUPABASE_URL = "https://your-project-id.supabase.co"  # <-- Swap with your Data API URL
SUPABASE_KEY = "sb_publishable_zuVB7GExn16WwzWIjLrGzw_jCspPzyK"

class TabComms(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize connection
        print("[⚡] Connecting to cloud cluster...")
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("[✓] Supabase driver handshake initialized.")
        except Exception as e:
            print(f"[❌] Initialization crash: {e}")
            self.supabase = None

        # --- UI ELEMENTS ---
        ctk.CTkLabel(self, text="💬 Team Communications Feed", font=("Arial", 18, "bold")).pack(pady=10)

        # Message Scroll Area
        self.chat_feed = ctk.CTkScrollableFrame(self, width=600, height=350)
        self.chat_feed.pack(padx=20, pady=10, fill="both", expand=True)

        # Input Row
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=15)

        self.name_input = ctk.CTkEntry(input_frame, placeholder_text="Your Name...", width=150)
        self.name_input.pack(side="left", padx=(0, 10))

        self.msg_input = ctk.CTkEntry(input_frame, placeholder_text="Type a broadcast to your group...", width=600)
        self.msg_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.send_btn = ctk.CTkButton(input_frame, text="Send 🚀", width=100, command=self.send_message)
        self.send_btn.pack(side="right")

        # Initial background load
        self.refresh_feed()

    def refresh_feed(self):
        if not self.supabase:
            return

        def fetch_task():
            try:
                response = self.supabase.table("app_messages").select("*").order("created_at", descending=False).limit(50).execute()
                # Update UI elements safely back on the main Tkinter thread
                self.after(0, lambda: self.render_messages(response.data))
            except Exception as e:
                print(f"[❌] Could not fetch records from database: {e}")

        threading.Thread(target=fetch_task, daemon=True).start()

    def render_messages(self, messages):
        # Clear out previous widgets to avoid duplicate overlay rendering
        for widget in self.chat_feed.winfo_children():
            widget.destroy()

        if not messages:
            lbl = ctk.CTkLabel(self.chat_feed, text="No messages yet. Start the conversation!", font=("Arial", 12, "italic"), text_color="gray")
            lbl.pack(pady=20)
            return

        for msg in messages:
            sender = msg.get("sender_name", "Unknown")
            text = msg.get("message_text", "")
            
            msg_box = ctk.CTkFrame(self.chat_feed, fg_color="#2b2b2b", corner_radius=6)
            msg_box.pack(fill="x", pady=4, padx=5)
            
            lbl = ctk.CTkLabel(msg_box, text=f"👤 {sender}:  {text}", font=("Arial", 12), anchor="w", justify="left")
            lbl.pack(padx=10, pady=5, fill="x")

    def send_message(self):
        sender = self.name_input.get().strip()
        text = self.msg_input.get().strip()

        if not sender or not text:
            print("[⚠️] Send blocked: Name or message bar is empty.")
            return

        if not self.supabase:
            print("[❌] Send blocked: Supabase client connection is offline.")
            return

        # Snap clear the box so UI interactions feel fast
        self.msg_input.delete(0, "end")

        def send_task():
            try:
                print(f"[🚀] Uploading message row data -> Sender: '{sender}', Text: '{text}'")
                
                # Payload injection
                response = self.supabase.table("app_messages").insert({
                    "sender_name": sender,
                    "message_text": text
                }).execute()
                
                print(f"[✓] Server acknowledgement success! Data profile: {response.data}")
                
                # Immediately pull down fresh logs to update the layout frame
                self.after(0, self.refresh_feed)
                
            except Exception as e:
                print("\n[🚨] SUPABASE NETWORK TRANSMISSION ERROR DETECTED [🚨]")
                print("-" * 60)
                traceback.print_exc()
                print("-" * 60)

        threading.Thread(target=send_task, daemon=True).start()