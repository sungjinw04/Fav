from pyrogram import Client, filters
from pymongo import MongoClient
import os
from datetime import datetime

# Replace with your API ID, API HASH and Bot Token from BotFather
api_id = "25064357"
api_hash = "cda9f1b3f9da4c0c93d1f5c23ccb19e2"
bot_token = "7519139941:AAE6jFCGiqvhLu1i7HoNL9qdQRZgrQm6HqM"

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# MongoDB setup
mongo_client = MongoClient("mongodb+srv://Sungjinwoo4:9f3FShxbKgJF1U1o@cluster0.nynyp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client.telegram_bot
user_data = db.user_data

# Function to track and store user info
def track_user(user):
    user_doc = user_data.find_one({"user_id": user.id})
    if user_doc:
        # Check for changes
        changes = []
        if user.username != user_doc.get("username"):
            changes.append({
                "field": "username",
                "old_value": user_doc.get("username"),
                "new_value": user.username,
                "timestamp": datetime.utcnow().isoformat()
            })
        if user.first_name + " " + (user.last_name or "") != user_doc.get("name"):
            changes.append({
                "field": "name",
                "old_value": user_doc.get("name"),
                "new_value": user.first_name + " " + (user.last_name or ""),
                "timestamp": datetime.utcnow().isoformat()
            })
        if changes:
            # Update document with changes
            user_data.update_one({"user_id": user.id}, {"$set": {
                "username": user.username,
                "name": user.first_name + " " + (user.last_name or ""),
                "changes": user_doc.get("changes", []) + changes
            }})
            # Notify group about the changes
            for change in changes:
                app.send_message(user.chat.id, f"{user_doc.get('name')} has changed their {change['field']} to {change['new_value']}.")
    else:
        # Add new user
        user_data.insert_one({
            "user_id": user.id,
            "username": user.username,
            "name": user.first_name + " " + (user.last_name or ""),
            "changes": []
        })

# Handler to track new messages
@app.on_message(filters.group)
def capture_messages(client, message):
    user = message.from_user
    if user:
        track_user(user)

# Command to fetch all changes made by a particular member
@app.on_message(filters.command("balatkaar", prefixes="/") & filters.group)
def fetch_user_changes(client, message):
    user_id = message.command[1]  # Assuming the user_id is passed as an argument
    user_doc = user_data.find_one({"user_id": int(user_id)})
    if user_doc and "changes" in user_doc:
        changes = user_doc["changes"]
        if changes:
            change_msgs = [f"{change['field'].capitalize()} changed from {change['old_value']} to {change['new_value']} at {change['timestamp']}" for change in changes]
            client.send_message(message.chat.id, "\n".join(change_msgs))
        else:
            client.send_message(message.chat.id, "No changes recorded for this user.")
    else:
        client.send_message(message.chat.id, "User not found.")

if __name__ == "__main__":
    app.run()

