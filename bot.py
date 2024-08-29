import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message

# Initialize Pyrogram client
app = Client(
    "my_bot",
    api_id="25064357",  # Replace with your API ID
    api_hash="cda9f1b3f9da4c0c93d1f5c23ccb19e2"",  # Replace with your API hash
    bot_token="7519139941:AAE6jFCGiqvhLu1i7HoNL9qdQRZgrQm6HqM"  # Replace with your bot token
)

# Connect to SQLite database
conn = sqlite3.connect("postgres://avnadmin:AVNS_Ez0UFOgjgaSCk-Gr7NQ@sung-erenyeager.h.aivencloud.com:23096/defaultdb?sslmode=require")
cursor = conn.cursor()

def update_user_info(user_id, username, full_name):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        if user[1] != username:
            cursor.execute("INSERT INTO username_changes (user_id, old_username, new_username) VALUES (?, ?, ?)",
                           (user_id, user[1], username))
            conn.commit()
            return f"User @{user[1]} has changed their username to @{username}."
        
        if user[2] != full_name:
            cursor.execute("INSERT INTO fullname_changes (user_id, old_fullname, new_fullname) VALUES (?, ?, ?)",
                           (user_id, user[2], full_name))
            conn.commit()
            return f"User {user[2]} has changed their name to {full_name}."
        
        return None
    else:
        cursor.execute("INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                       (user_id, username, full_name))
        conn.commit()
        return None

@app.on_message(filters.group)
def capture_message(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.first_name + " " + (message.from_user.last_name or "")
    
    notification = update_user_info(user_id, username, full_name)
    if notification:
        message.reply_text(notification)

@app.on_message(filters.command("balatkaar") & filters.group)
def fetch_changes(client, message: Message):
    if len(message.command) > 1:
        user_id = message.command[1]
        cursor.execute("SELECT old_username, new_username, change_time FROM username_changes WHERE user_id = ?", (user_id,))
        username_changes = cursor.fetchall()
        
        cursor.execute("SELECT old_fullname, new_fullname, change_time FROM fullname_changes WHERE user_id = ?", (user_id,))
        fullname_changes = cursor.fetchall()
        
        response = "Username changes:\n" + "\n".join([f"{old} -> {new} at {time}" for old, new, time in username_changes])
        response += "\n\nFullname changes:\n" + "\n".join([f"{old} -> {new} at {time}" for old, new, time in fullname_changes])
        
        message.reply_text(response)
    else:
        message.reply_text("Please provide a user ID.")

# Run the bot
app.run()

