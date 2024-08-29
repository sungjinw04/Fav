import sqlite3
from pyrogram import Client, filters

# Initialize the bot with your credentials
API_ID = "25064357"
API_HASH = "cda9f1b3f9da4c0c93d1f5c23ccb19e2"
BOT_TOKEN = "7519139941:AAE6jFCGiqvhLu1i7HoNL9qdQRZgrQm6HqM"

app = Client("link_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            link TEXT
        )
    """)
    conn.commit()
    conn.close()

# Command to save a link
@app.on_message(filters.command("link") & filters.private)
async def save_link(client, message):
    user_id = message.from_user.id
    if len(message.command) > 1:
        link = message.command[1]
    else:
        await message.reply_text("Please provide a link. Usage: /link {link}")
        return

    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO links (user_id, link) VALUES (?, ?)", (user_id, link))
    conn.commit()
    conn.close()
    if rows:
        links = "\n".join([row[0] for row in rows])
        message.reply_text(f"Your saved links:\n{links}")
    else:
        message.reply_text("You haven't saved any links yet.")

# Initialize the database when the bot starts
if __name__ == "__main__":
    init_db()
    app.run()

