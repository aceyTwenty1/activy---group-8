import customtkinter as ctk
import threading
from supabase import create_client, Client

# --- CLOUD CONFIGURATION ---
# Get these credentials from your Supabase Project Settings -> API page
SUPABASE_URL = "https://jasmjpxryuhdxgndwyvk.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_zuVB7GExn16WwzWIjLrGzw_jCspPzyK"

class TabComms(ctk.CTkFrame):
    def __init__(self, parent, db_handler):
        super().__init__(parent, fg_color="transparent")
        
        # Connect to your cloud database cluster
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception:
            self.supabase = None

        # --- UI LAYOUT ---
        ctk.CTkLabel(self, text="💬 Team Communications Feed", font=("Arial", 18, "bold")).pack(pady=10)

        # Scrollable area to view live messages
        self.chat_feed = ctk.CTkScrollableFrame(self, width=600, height=350)
        self.chat_feed.pack(padx=20, pady=10, fill="both", expand=True)

        # Input Frame container at the bottom
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=15)

        # Sender Name input
        self.name_input = ctk.CTkEntry(input_frame, placeholder_text="Your Name...", width=150)
        self.name_input.pack(side="left", padx=(0, 10))

        # Message Text input
        self.msg_input = ctk.CTkEntry(input_frame, placeholder_text="Type a broadcast to your group...", width=600)
        self.msg_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Send Button
        self.send_btn = ctk.CTkButton(input_frame, text="Send 🚀", width=100, command=self.send_message)
        self.send_btn.pack(side="right")

        # Load existing chat logs on startup
        self.refresh_feed()

    def refresh_feed(self):
        if not self.supabase:
            return

        # Clear existing labels in the UI feed frame
        for widget in self.chat_feed.winfo_children():
            widget.destroy()

        def fetch_task():
            try:
                # Grab the last 50 messages from Oracle Cloud / Supabase hardware
                response = self.supabase.table("app_messages").select("*").order("created_at", descending=False).limit(50).execute()
                messages = response.data

                # Loop back to the main GUI thread to draw them safely
                self.after(0, lambda: self.render_messages(messages))
            except Exception as e:
                print(f"Failed to fetch global chat logs: {e}")

        # Run web requests in a background thread so the app doesn't freeze
        threading.Thread(target=fetch_task, daemon=True).start()

    def render_messages(self, messages):
        for msg in messages:
            sender = msg.get("sender_name", "Anonymous")
            text = msg.get("message_text", "")
            
            # Format: "Sender: Message Content"
            msg_box = ctk.CTkFrame(self.chat_feed, fg_color="#2b2b2b", corner_radius=6)
            msg_box.pack(fill="x", pady=4, padx=5)
            
            lbl = ctk.CTkLabel(
                msg_box, 
                text=f"👤 {sender}:  {text}", 
                font=("Arial", 12),
                anchor="w",
                justify="left"
            )
            lbl.pack(padx=10, pady=5, fill="x")

    def send_message(self):
        sender = self.name_input.get().strip()
        text = self.msg_input.get().strip()

        if not sender or not text or not self.supabase:
            return

        # Clear out message input bar right away for snappy feel
        self.msg_input.delete(0, "end")

        def send_task():
            try:
                # Fire row record straight to the cloud
                self.supabase.table("app_messages").insert({
                    "sender_name": sender,
                    "message_text": text
                }).execute()
                
                # Refresh layout elements locally
                self.after(0, self.refresh_feed)
            except Exception as e:
                print(f"Network delivery error: {e}")

        threading.Thread(target=send_task, daemon=True).start()