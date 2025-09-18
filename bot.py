import json 
import io
import numpy as np
import PyPDF2
import google.generativeai as genai
from flask import Flask
import asyncio
import shlex
import asyncpg
import os
from telegram import Update, Document, Bot
import logging
import shlex
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler,ConversationHandler,
    ContextTypes, filters, Application
)
#from secretspy import GMAIL_USER, GMAIL_APP_PASSWORD
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, time
import sys
import random 
import re
from functools import wraps
from apscheduler.schedulers.asyncio import AsyncIOScheduler
flask_app= Flask(__name__)
@flask_app.route("/")
def home():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ENP Course Material Bot</title>
    <style>
        :root {
            --main-bg: #ffffff;
            --text-color: #222222;
            --card-bg: #f0f4f8;
            --accent: #005dce;
            --accent-hover: #004bb5;
            --border-radius: 8px;
            --transition: 0.3s;
            --max-width: 900px;
        }

        [data-theme="dark"] {
            --main-bg: #121212;
            --text-color: #e0e0e0;
            --card-bg: #1f1f1f;
            --accent: #3399ff;
            --accent-hover: #0066cc;
        }

        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: var(--main-bg);
            background-image: url('https://www.enp.edu.dz/storage/elementor/thumbs/20150509_080335-1-owt6moufw06fnk0t8q1eeeg62jsavcwpteq4f9vhrs.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
            transition: background var(--transition), color var(--transition);
        }

        main {
            max-width: var(--max-width);
            width: 100%;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: var(--border-radius);
            box-shadow: 0 0 20px rgba(0,0,0,0.08);
            text-align: center;
        }

        h1 {
            color: var(--accent);
            margin-top: 0;
        }

        .tagline {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            font-weight: 400;
        }

        .commands {
            text-align: left;
            margin-top: 2rem;
        }

        .commands h2 {
            margin-bottom: 1rem;
            color: var(--accent);
        }

        ul.command-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        ul.command-list li {
            margin: 0.8rem 0;
            padding: 1rem;
            background: var(--main-bg);
            border-left: 4px solid var(--accent);
            border-radius: var(--border-radius);
            display: flex;
            align-items: center;
        }

        ul.command-list code {
            font-weight: bold;
            color: var(--accent);
            background: rgba(0, 93, 206, 0.1);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            margin-right: 0.5rem;
            flex-shrink: 0;
        }

        .button {
            display: inline-block;
            margin-top: 2rem;
            background: var(--accent);
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            border-radius: var(--border-radius);
            text-decoration: none;
            font-weight: bold;
            transition: background var(--transition);
        }

        .button:hover {
            background: var(--accent-hover);
        }

        footer {
            margin-top: 3rem;
            font-size: 0.9rem;
            color: #888888;
        }

        footer a {
            color: var(--accent);
            text-decoration: none;
            margin: 0 0.5rem;
        }

        .theme-toggle {
            position: absolute;
            top: 1rem;
            right: 1rem;
            cursor: pointer;
            font-size: 0.9rem;
            background: var(--card-bg);
            padding: 0.4rem 0.8rem;
            border-radius: var(--border-radius);
            border: 1px solid #cccccc;
            user-select: none;
        }

        @media (max-width: 600px) {
            main {
                padding: 1rem;
            }
            body {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme">🌙</button>
    <main role="main">
        <h1>📚 ENP Course Material Bot</h1>
        <p class="tagline">Your assistant to access, upload, and manage ENP study files directly on Telegram.</p>
        <a class="button" href="https://t.me/ENPcoursebot" target="_blank" rel="noopener noreferrer">🚀 Open @ENPcoursebot on Telegram</a>

        <section class="commands">
            <h2>📖 Bot Commands</h2>
            <ul class="command-list" aria-label="List of available bot commands">
                <li><code>/start</code> — Welcome message</li>
                <li><code>/help</code> — Show help menu</li>
                <li><code>/upload &lt;module&gt; &lt;category&gt;</code> — Upload a file (admins only)</li>
                <li><code>/done</code> — Reset upload state after you're done</li>
                <li><code>/get &lt;module&gt; &lt;category&gt;</code> — Retrieve saved files</li>
                <li><code>/delete &lt;filename&gt;</code> — Delete file by name (admins only)</li>
                <li><code>/search &lt;keyword&gt;</code> — Search for matching keywords</li>
                <li><code>/credits</code> — Project owner + contact</li>
                <li><code>/register</code> — Register using enp email</li>
                <li><code>/askai</code> — Ask the gemini‑2‑Pro model about any files in the database</li>
            </ul>
        </section>

        <footer>
            Made by <strong>Fadeli Ala Eddine</strong> <br />
            Contact: <a href="mailto:enpcoursebot@gmail.com">enpcoursebot@gmail.com</a>
            <div>
                <a href="https://github.com/AlaFadeli" target="_blank" rel="noopener noreferrer">GitHub</a>
                •
                <a href="https://t.me/ENPcoursebot" target="_blank" rel="noopener noreferrer">Telegram Bot</a>
            </div>
        </footer>
    </main>

    <script>
        function toggleTheme() {
            const current = document.documentElement.getAttribute("data-theme");
            const next = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            localStorage.setItem("theme", next);
        }

        // Apply previously saved theme
        const storedTheme = localStorage.getItem("theme") || "light";
        document.documentElement.setAttribute("data-theme", storedTheme);
    </script>
</body>
</html>"""
# ...existing code...
````
Next steps: review the updated HTML for any missing assets or accessibility tweaks you’d like to add.

## Me

edit it on file

## CodeCompanion (OpenAI)

```python
# filepath: bot.py
# ...existing code...
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ENP Course Material Bot</title>
    <style>
        :root {
            --main-bg: #ffffff;
            --text-color: #222222;
            --card-bg: #f0f4f8;
            --accent: #005dce;
            --accent-hover: #004bb5;
            --border-radius: 8px;
            --transition: 0.3s;
            --max-width: 900px;
        }

        [data-theme="dark"] {
            --main-bg: #121212;
            --text-color: #e0e0e0;
            --card-bg: #1f1f1f;
            --accent: #3399ff;
            --accent-hover: #0066cc;
        }

        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: var(--main-bg);
            background-image: url('https://www.enp.edu.dz/storage/elementor/thumbs/20150509_080335-1-owt6moufw06fnk0t8q1eeeg62jsavcwpteq4f9vhrs.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
            transition: background var(--transition), color var(--transition);
        }

        main {
            max-width: var(--max-width);
            width: 100%;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: var(--border-radius);
            box-shadow: 0 0 20px rgba(0,0,0,0.08);
            text-align: center;
        }

        h1 {
            color: var(--accent);
            margin-top: 0;
        }

        .tagline {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            font-weight: 400;
        }

        .commands {
            text-align: left;
            margin-top: 2rem;
        }

        .commands h2 {
            margin-bottom: 1rem;
            color: var(--accent);
        }

        ul.command-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        ul.command-list li {
            margin: 0.8rem 0;
            padding: 1rem;
            background: var(--main-bg);
            border-left: 4px solid var(--accent);
            border-radius: var(--border-radius);
            display: flex;
            align-items: center;
        }

        ul.command-list code {
            font-weight: bold;
            color: var(--accent);
            background: rgba(0, 93, 206, 0.1);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            margin-right: 0.5rem;
            flex-shrink: 0;
        }

        .button {
            display: inline-block;
            margin-top: 2rem;
            background: var(--accent);
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            border-radius: var(--border-radius);
            text-decoration: none;
            font-weight: bold;
            transition: background var(--transition);
        }

        .button:hover {
            background: var(--accent-hover);
        }

        footer {
            margin-top: 3rem;
            font-size: 0.9rem;
            color: #888888;
        }

        footer a {
            color: var(--accent);
            text-decoration: none;
            margin: 0 0.5rem;
        }

        .theme-toggle {
            position: absolute;
            top: 1rem;
            right: 1rem;
            cursor: pointer;
            font-size: 0.9rem;
            background: var(--card-bg);
            padding: 0.4rem 0.8rem;
            border-radius: var(--border-radius);
            border: 1px solid #cccccc;
            user-select: none;
        }

        @media (max-width: 600px) {
            main {
                padding: 1rem;
            }
            body {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme">🌙</button>
    <main role="main">
        <h1>📚 ENP Course Material Bot</h1>
        <p class="tagline">Your assistant to access, upload, and manage ENP study files directly on Telegram.</p>
        <a class="button" href="https://t.me/ENPcoursebot" target="_blank" rel="noopener noreferrer">🚀 Open @ENPcoursebot on Telegram</a>

        <section class="commands">
            <h2>📖 Bot Commands</h2>
            <ul class="command-list" aria-label="List of available bot commands">
                <li><code>/start</code> — Welcome message</li>
                <li><code>/help</code> — Show help menu</li>
                <li><code>/upload &lt;module&gt; &lt;category&gt;</code> — Upload a file (admins only)</li>
                <li><code>/done</code> — Reset upload state after you're done</li>
                <li><code>/get &lt;module&gt; &lt;category&gt;</code> — Retrieve saved files</li>
                <li><code>/delete &lt;filename&gt;</code> — Delete file by name (admins only)</li>
                <li><code>/search &lt;keyword&gt;</code> — Search for matching keywords</li>
                <li><code>/credits</code> — Project owner + contact</li>
                <li><code>/register</code> — Register using enp email</li>
                <li><code>/askai</code> — Ask the gemini‑2‑Pro model about any files in the database</li>
            </ul>
        </section>

        <footer>
            Made by <strong>Fadeli Ala Eddine</strong> <br />
            Contact: <a href="mailto:enpcoursebot@gmail.com">enpcoursebot@gmail.com</a>
            <div>
                <a href="https://github.com/AlaFadeli" target="_blank" rel="noopener noreferrer">GitHub</a>
                •
                <a href="https://t.me/ENPcoursebot" target="_blank" rel="noopener noreferrer">Telegram Bot</a>
            </div>
        </footer>
    </main>

    <script>
        function toggleTheme() {
            const current = document.documentElement.getAttribute("data-theme");
            const next = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            localStorage.setItem("theme", next);
        }

        // Apply previously saved theme
        const storedTheme = localStorage.getItem("theme") || "light";
        document.documentElement.setAttribute("data-theme", storedTheme);
    </script>
</body>
</html>"""
def run_flask():
    port =int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
def load_token_file(path="token.txt"):
    with open(path,"r") as file:
        return file.read().strip()
API_TOKEN= os.getenv("API_TOKEN")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
#ADMIN1= os.getenv("ADMIN1")
#ADMIN2= os.getenv("ADMIN2")
#ADMIN3= os.getenv("ADMIN3")
#ADMIN4= os.getenv("ADMIN4")
ADMIN1 = 5655037405
ADMIN2 = 5637922495
ADMIN3 = 5131542154
ADMIN4 = 5632596557
ADMIN_ID=[ADMIN1, ADMIN2, ADMIN3, ADMIN4]
upload_state = {}
#def get_base(path="databaseurl.txt"):
#    with open(path,"r") as f:
#        return f.read().strip()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    print("url:", DATABASE_URL)
async def connect_db():
    return await asyncpg.connect(DATABASE_URL)
ASK_EMAIL, ASK_CODE = range(2)
#async def connect_db():
#    global db_conn
#    db_conn = await asyncpg.connect(DATABASE_URL)   

def send_verification_email(to_email,code):
    msg = MIMEText(f"""\
    Hello,
    Thank you for registering with the ENP Course Assistant Bot.
    Your verification code is: {code}"

    It's valid for 10 minutes. if you did not request this, you can simply ignore the email.
    This is an automated email. Please don't reply.



    Best regards,
    """)
    msg['Subject'] = "ENP  Bot Verification Code"
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
#HELPER FUNCTIONS for database
async def save_material(module, category, file_name, file_id):
    conn = await connect_db()
    await conn.execute("""
        INSERT INTO materials (module, category, file_name, file_id)
        VALUES ($1, $2, $3, $4)
    """, module, category, file_name, file_id)
    await conn.close()
async def get_all_materials():
    conn = await connect_db()
    rows = await conn.fetch("SELECT * FROM materials")
    await conn.close()
    return rows
async def delete_material_by_filename(file_name):
    conn = await connect_db()
    result = await conn.execute("""
        DELETE FROM materials WHERE file_name =  $1
    """, file_name.strip())
    await conn.close()
    return result
async def find_material_by_filename(file_name):
    conn = await connect_db()
    row = await conn.fetchrow("""
        SELECT * FROM materials WHERE file_name = $1
    """, file_name)
    await conn.close()
    return row
async def is_verified(user_id, db_conn):
    result = await db_conn.fetchrow(
    "SELECT is_verified FROM verified_users WHERE user_id = $1"
    ,user_id)
    return result and result["is_verified"]
def registered_only(func):
    @wraps(func)
    async def wrapper(update:Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        db_conn =await connect_db()
        if not await is_verified(user_id, db_conn):
            await update.messagee.reply_text("You are not registered. Use /register first.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper    
async def get_users_to_remind():
    conn = await connect_db()
    users = await conn.fetch("SELECT user_id, username FROM verified_users WHERE reminder_due = TRUE")
    await conn.close()
    return users
async def send_reminders(bot: Bot):
    users = await get_users_to_remind()
    for user in users:
        try:
            await bot.send_message(
                chat_id=user["user_id"],
                text=f"Hi {user['username']}, this is your reminder, DID YOU QUIT STUDYING ????!!!!"
            )
            logging.info(f"Sent reminder to {user['username']}")
        except Exception as e:
            logging.error(f"Failed to send reminder to {user['user_id']}:{e}")
 
async def start_scheduler(app: Application):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, "interval", days=2, args=[app.bot])
    scheduler.start()
#initial start command

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_conn = await connect_db()
    await update.message.reply_text( """👋 WELCOME, future Hunter !
This is version 1.0.0 of ENP Course Assistant Bot!    
⚙️ Type /help to explore tools  
📝 Don’t forget to /register before using commands.""")
    await log_usage(update.effective_user.id, update.effective_user.username, "/start", update.effective_chat.id)
@registered_only
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN1 and user_id != ADMIN2 and user_id !=  ADMIN3 and user_id != ADMIN4:
        return await update.message.reply_text('You are not authorized to upload, get a promotion or get used to it :)')
    db_conn = await connect_db()
    user_id = update.effective_user.id
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    if len(context.args) != 2:
        return await update.message.reply_text("Wrong sytanx :( , usage: /upload <module> <category> ")
    module,category = context.args
    upload_state[update.effective_user.id] = (module,category)
    await update.message.reply_text(f"Upload target set to :  {module} > {category}\nNow send me the file!")    
# for get file command again we use async
@registered_only
async def get_files(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_conn = await connect_db()
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    if len(context.args) != 2:
        return await update.message.reply_text("Worng syntax :( , usage:/get <module> <category>")
    module, category = context.args
    rows = await get_all_materials()
    matched = [row for row in rows if row ['module'] == module and row['category'] == category]
    if not matched:
        return await update.message.reply_text("No files found in this category")
    for row in matched:
        await update.message.reply_document(document=row['file_id'], caption=row['file_name'])
    # as usual for ANY command : async
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_conn = await connect_db()
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    user_id = update.effective_user.id    
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    # only admins can upload : 
    if user_id not in  ADMIN_ID:
        await update.message.reply_text("Only the admins can play with files :)  respect yourself !!!!")
        return 
    if user_id not in upload_state:
        await update.message.reply_text("Use upload <module> <type> first.")
        return
    list_docs = []
    document = update.message.document
    list_docs.append(document)
    if not document:
        return await update.message.reply_text("No document found in the message.....")
    module,category = upload_state[user_id]
    file_id = document.file_id
    file_name = document.file_name or f"file_{file_id[:6]}"
    if upload_state[user_id]:
        for document in list_docs:
            await save_material(module, category, file_name, file_id)
            await update.message.reply_text(f"File Saved!\nModule:{module}\nType: {category}\nName:{file_name}")
    # clean and update
async def help_command(update:Update, context = ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_conn = await connect_db()
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    user_id = update.effective_user.id    
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    commands = """
        *ENP Course Material Bot commands:*
        /start -Welcome message
        /help  -show this current help menu
        /upload <module> <category> -Sets target to upload a file (for admins only) 
        /done  -- resets upload state -Do it after done from uploading files
        /get <module> <category> -Retrieve saved files 
        /delete <filename> -deletes file name (for admins only)
        /search <keyword> -searchs for matching words 
        /credits - project owner + contact
            note: After /upload ,send your file directly.
        """
    await update.message.reply_text(commands, parse_mode="Markdown")
    await log_usage(update.effective_user.id, update.effective_user.username, "/help", update.effective_chat.id)
@registered_only       
async def delete_file(update:Update, context = ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_conn = await connect_db()
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    if update.effective_user.id not in ADMIN_ID:
        return await update.message.reply_text("You are not authorized to delete files")
    if not context.args:
        return await update.message.reply_text("Usage: /delete <filename>")
    file_names = shlex.split(" ".join(context.args))
    if not file_names:
        return await update.message.reply_text("Usage: /delete <filename1> <filename2>....")
    responses = []
    for file_name in file_names:
        file_name = file_name.strip()
        deleted = await delete_material_by_filename(file_name)
        if deleted :
            responses.append(f"Deleted `{file_name}`")
        else:
            responses.append(f"Not found `{file_name}`")
    await update.message.reply_text("\n".join(responses), parse_mode="Markdown")
@registered_only       
async def search_command(update:Update, context=ContextTypes.DEFAULT_TYPE):
    db_conn = await asyncpg.connect(DATABASE_URL)
    user_id = update.effective_user.id    
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    if not context.args:
        return await update.message.reply_text(" Usage: /search <keyword>")
    keyword = " ".join(context.args).lower()
    rows = await get_all_materials()
    matched = [row for row in rows if keyword in row['file_name']] 
    if not matched:
        await update.message.reply_text(f"No files found for `{keyword}`")
    response = f"*Found {len(matched)} file(s):*\n\n"
    for row in matched:
        response += f"📁{row['module']} --> 📘{row['category']} -->📄{row['category']} --> {row['file_name']}\n"
    await update.message.reply_text(response, parse_mode="Markdown")    
    await log_usage(update.effective_user.id, update.effective_user.username, "search", update.effective_chat.id)
async def credits_command(update:Update, context=ContextTypes.DEFAULT_TYPE):           
    user_id = update.effective_user.id
    db_conn = await connect_db()
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    crrds = """
        *Bot Credits*
        \\-see more projects on my Github \: https\:\/\/github\\.com/AlaFadeli"
        \\-Contact me via email \:  ala\_eddine\\.fadeli@g\\.enp\\.edu\\.dz"
        \\-report an issue \: enpcourse\\.bot@gmail\\.com"
        \\-project launch date \: 2025\\-07\\-19" """
    await update.message.reply_text(crrds, parse_mode='MarkdownV2')
    await log_usage(update.effective_user.id, update.effective_user.username, "credits", update.effective_chat.id)
@registered_only       
async def admin_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id    
    if not await is_verified(user_id, db_conn):
        return await update.message.reply_text(" You need to register first using /register")
    user_id = update.effective_user.id
    print("Your ID:", user_id)
    print("Admin list", ADMIN_ID)
    if user_id not in ADMIN_ID:
        await update.message.reply_text("You are not authorized to view admin list")    
    return await update.message.reply_text(" You are  authorized, admin")    
@registered_only       
async def list_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id    
    module, category = context.args 
    if len(context.args) != 2:
        return await update.message.reply_text("Worng syntax :( , usage: /search <module> <category>")
    rows = await get_all_materials()
    message = "A list of available files in this module:"
    matched = [row for row in rows if row ['module'] == module and row['category'] == category]
    for row in matched :
        await update.message.reply_text(f"--> {row['file_name']}\n")
    await log_usage(update.effective_user.id, update.effective_user.username, "/list", update.effective_chat.id)
@registered_only       
async def done_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in upload_state:
        del upload_state[user_id]
        await update.message.reply_text("Upload session ended.")
    else:
        await update.message.reply_text("No active upload  session")
async def receive_email(update:Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    if not re.fullmatch(r"[a-z0-9._%+-]+@g\.enp\.edu\.dz", email):
        await update.message.reply_text("That doesn't look like a valid ENP  email address ...")
        return ASK_EMAIL
    code = str(random.randint(100000,999999))
    context.user_data['email'] = email
    context.user_data['code'] = code
    send_verification_email(email,code)
    await update.message.reply_text(f"Verification code sent to `{email}`. Please reply with it to complete verification", parse_mode='Markdown')
    return ASK_CODE
async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text.strip()
    correct_code = context.user_data.get('code')
    if user_code == correct_code:
        await update.message.reply_text("Email verified successfully, enjoy the bot ENP warior !")
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        email = context.user_data["email"]
        db_conn= await connect_db()
        await db_conn.execute("""
              
            INSERT INTO verified_users(user_id, username, email, is_verified, verified_at)
            VALUES ($1, $2, $3, TRUE, now()) 
            ON CONFLICT (user_id)  DO UPDATE SET username = EXCLUDED.username,
                                                 email = EXCLUDED.email,
                                                 is_verified = TRUE,
                                                 verified_at = now()
        """,
        user_id, username, email)
        await db_conn.close()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Wrong code. Please try again")

        return ASK_CODE
async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter your email adress")
    await log_usage(update.effective_user.id, update.effective_user.username, "register", update.effective_chat.id)
    return ASK_EMAIL
conv_handler = ConversationHandler(entry_points= [CommandHandler("register", register_command)],
                                states = {
                                    ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
                                    ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_code)],
                                },
                                fallbacks = [],
)



# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

# Connect to DB
async def connect_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"))

# Get file_id from DB
async def get_file_id(file_name):
    conn = await connect_db()
    row = await conn.fetchrow("SELECT file_id FROM materials WHERE file_name = $1", file_name)
    await conn.close()
    return row["file_id"] if row else None

# Extract PDF text chunks
def extract_chunks_from_pdf(pdf_bytes, max_chars=3000):
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
        if len(full_text) > max_chars:
            break
    chunks = [full_text[i:i+1000] for i in range(0, len(full_text), 1000)]
    return chunks[:3]  # limit to 3 chunks max for prompt size
# markdownv2 
# /askai command handler
@registered_only
async def askai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await log_usage(update.effective_user.id, update.effective_user.username, "/askai", update.effective_chat.id)
    text = update.message.text or ""
    args = shlex.split(text)
    if len(args) < 3:
        await update.message.reply_text("Usage: /askai \"File name.pdf \" Your question here ")
        return 
    file_name = args[1]
    user_question = " ".join(args[2:])

    file_id = await get_file_id(file_name)
    if not file_id:
        await update.message.reply_text("File not found in the database.")
        return

    # Download file from Telegram
    file = await context.bot.get_file(file_id)
    file_bytes = await file.download_as_bytearray()

    # Extract chunks
    chunks = extract_chunks_from_pdf(file_bytes)
    context_text = "\n\n".join(chunks)

    # Prepare prompt
    prompt = f"""You are a distinguished academic assistant and subject-matter expert. Your role is to help students master complex concepts using only the material provided. Please adhere strictly to the following instructions:

1. Use Only Provided Context  
   – Do not draw on any external knowledge.  
   – Base your entire answer on the excerpts below.

2. Professional Tone & Clarity  
   – Respond in clear, concise, and formal academic English.  
   – Structure your answer with a brief introduction, key points (using numbered or bulleted lists when appropriate), and a concise summary.

3. Visual Illustration (Optional)  skip this for now 
   – If the concept can be made clearer by a diagram, chart, or photo, embed a relevant image using Markdown syntax:  
     ![Alt text](<image_url_or_placeholder>)  
   – If you don’t have an actual URL, use a placeholder like <diagram_of_[concept]> to indicate where an image would go.

4. Honesty & Limitations  
   – If the answer is not fully supported by the context, say:  
     *“I couldn’t find a definitive answer in the provided material.”*
notes: Add emojis for interactive and fun response, use a fun yet Professional tone
        
Content:
{context_text}

Question:
{user_question}
"""

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text.strip())
    except Exception as e:
        await update.message.reply_text("Error: " + str(e))
async def get_users(): 
    conn = await connect_db()
    users = await conn.fetch("SELECT user_id FROM verified_users WHERE is_verified = TRUE")
    await conn.close()
    return users
from datetime import timedelta

async def log_usage(user_id, username, command, chat_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO bot_usage (user_id,username,command,chat_id,used_at) VALUES ($1, $2, $3, $4, $5)",
        user_id, username, command, chat_id, datetime.utcnow()
    )
    await conn.close()
async def add_expense(update:Update,context:ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /expense <amount> <category> [description(optional)]")
        return 
    amount = float(args[0])
    category = args[1]
    description = " ".join(args[2:]) if len(args) > 2 else ""
    user_id = update.message.from_user.id
    conn = await connect_db()
    await conn.execute(
        "INSERT INTO expenses (user_id, amount, category, description) VALUES ($1, $2, $3, $4)",
        user_id, amount, category, description)
    
    await conn.close()
    await update.message.reply_text(f"Saved {amount} to {category}")

async def  summary(update:Update, context:ContextTypes.DEFAULT_TYPE):
    period = context.args[0] if context.args else "month"
    user_id = update.message.from_user.id

    conn = await connect_db()
    if period == "today":
        query = "SELECT category, SUM(amount) FROM expenses WHERE user_id=$1 AND date=CURRENT_DATE GROUP BY category"
    elif period == "week":
        query = "SELECT category, SUM(amount) FROM expenses WHERE user_id=$1 AND date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY category"
    else:
        query  = "SELECT category, SUM(amount) FROM expenses WHERE user_id=$1 AND date >= date_trunc('month', CURRENT_DATE) GROUP BY category"
    rows = await conn.fetch(query, user_id)
    await conn.close()
    if not rows :
        await update.message.reply_text("No expenses found")
    msg = "\n".join([f"{r['category']}:{r['sum']}" for r in rows])
    await update.message.reply_text(f"Expenses({period}):\n{msg}")
import matplotlib.pyplot as plt
import io
async def show_chart(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = await connect_db()
    rows = await conn.fetch("SELECT category, SUM(amount) AS total FROM expenses WHERE user_id=$1 GROUP BY category",
                            user_id)
    rows_months = await conn.fetch("""
      SELECT DATE_TRUNC('month', date) AS month, SUM(amount) AS total FROM expenses WHERE user_id=$1 GROUP BY month ORDER BY month""",
                                   user_id)
    rows_overtheweek = await conn.fetch("""SELECT DATE(date) AS day,SUM(amount) AS total FROM expenses WHERE user_id=$1 AND date >= (CURRENT_DATE - INTERVAL '6 days') GROUP BY day ORDER by day""", user_id)
    sleep_rows = await conn.fetch("""SELECT DATE(date) AS day, amount AS amount FROM sleep WHERE user_id=$1 ORDER BY date ASC""", user_id)
    
    await conn.close()
    if not rows:
        await update.message.reply_text("No expenses found yet")
    categories = [r["category"] for r in rows]
    totals = [float(r["total"]) for r in rows]
    months = [datetime.strftime(row["month"], "%b%Y") for row in rows_months]
    months_amounts = [float(row["total"]) for row in rows_months]
    days = [row["day"] for row in rows_overtheweek]
    days_amount = [float(row["total"]) for row in rows_overtheweek]
    today = datetime.utcnow().date()
    last7 = [(today - timedelta(days=i)) for i in range(6,-1,-1)]
    days_labels = [d.strftime('%a %d') for d in last7]
    days_totals = []
    data_map = {row["day"]: float(row["total"]) for row in rows_overtheweek}
    for d in last7:
        days_totals.append(data_map.get(d,0.0))
    #PIE CHART : categories
    plt.figure(figsize=(5,5))
    plt.pie(totals, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Expense Categories Breakdown")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf, caption="Here's your category chart!")
    #MONTHLY bar chart
    fig1, ax1 = plt.subplots()
    ax1.bar(months, months_amounts)
    ax1.set_title("Monthly Spending")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total Spent")
    ax1.tick_params(axis='x', rotation=45)
    buf1 = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf1, caption="Here's your monthly expenses")
    plt.close(fig1)

    #WEEKLY LINE CHART
    fig2, ax2= plt.subplots()
    ax2.plot(days_labels, days_totals, marker='o', linestyle='-', linewidth=2)
    ax2.set_title("Last 7 Days Spending")
    ax2.set_xlabel("Day")
    ax2.set_ylabel("Total Spent")
    ax2.grid(True, linestyle='--', alpha=0.5)
    buf2 = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf2, caption="Here's your last 7 days spending report")
    plt.close(fig2)
import pandas as pd
async def add_sleep(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 2 :
        await update.message.reply_text("Usage: /add_sleep [Amount (in hours)] [description (Bad, Good, Normal)]") 
    amount = float(context.args[0]) 
    description = context.args[1]
    conn = await connect_db()
    await conn.execute("INSERT INTO sleep(user_id, amount, description) VALUES ($1, $2, $3)",
                 user_id, amount, description
)
    conn.close()

async def show_sleep(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = await connect_db()

    sleep_rows = await conn.fetch("""SELECT DATE(date) AS day, amount AS amount FROM sleep WHERE user_id=$1 ORDER BY date ASC""", user_id)
    sleep_days = [row["day"] for row in sleep_rows]
    sleep_amount = [float(row["amount"]) for row in sleep_rows]
    conn.close()
    fig3, ax3 = plt.subplots()
    ax3.plot(sleep_days, sleep_amount, marker='o', linestyle='-', linewidth=2)
    ax3.set_title("Sleep tracking graph")
    ax3.set_xlabel("Day")
    ax3.set_ylabel("Sleep hours")
    ax3.grid(True, linestyle='--', alpha=0.5)
    buf3 = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf3, format='png')
    buf3.seek(0)
    await context.bot.send_photo(chat_id=user_id,photo=buf3, caption="Here's your sleep report for the last days")
    plt.close(fig3)
async def add_sport(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /add_sport [amount in mins] [laps (int)] [average impression (Good or Bad)]"
        )
        return
    amount = float(context.args[0])
    laps = int(context.args[1])
    description = context.args[2]

    conn = await connect_db()
    await conn.execute(
        """
        INSERT INTO sports(user_id, amount, description, laps)
        VALUES ($1, $2, $3, $4)
        """,
        user_id,
        amount,
        description,
        laps,
    )
    await conn.close()
    await update.message.reply_text("Today's sport session saved! …")
async def show_sport(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id 
    conn = await connect_db()

    # Minutes plot
    sport_rows = await conn.fetch(
        """
        SELECT DATE(date) AS day, amount
        FROM sports
        WHERE user_id = $1
        ORDER BY date ASC
        """,
        user_id,
    )
    sport_days = [row["day"] for row in sport_rows]
    sport_amount = [float(row["amount"]) for row in sport_rows]

    fig, ax = plt.subplots()
    ax.plot(sport_days, sport_amount, marker="o", linestyle="-", linewidth=2)
    ax.set_title("Sport tracking graph")
    ax.set_xlabel("Day")
    ax.set_ylabel("Sport mins")
    ax.grid(True, linestyle="--", alpha=0.5)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    await context.bot.send_photo(chat_id=user_id, photo=buf, caption="Here's your sport report for the last days")
    plt.close(fig)

    # Laps plot
    laps_rows = await conn.fetch(
        """
        SELECT DATE(date) AS day, laps
        FROM sports
        WHERE user_id = $1
        ORDER BY date ASC
        """,
        user_id,
    )
    laps_days = [row["day"] for row in laps_rows]
    sport_laps = [float(row["laps"]) for row in laps_rows]

    fig2, ax2 = plt.subplots()
    ax2.plot(laps_days, sport_laps, marker="o", linestyle="-", linewidth=2)
    ax2.set_title("Sport laps tracking graph")
    ax2.set_xlabel("Day")
    ax2.set_ylabel("Sport laps")
    ax2.grid(True, linestyle="--", alpha=0.5)
    buf2 = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf2, format="png")
    buf2.seek(0)
    await context.bot.send_photo(chat_id=user_id, photo=buf2, caption="Laps overview for the last days")
    plt.close(fig2)

    await conn.close()

async def add_study(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 2:
        update.message.reply_text("Usage: /add_study [AMOUNT (in hours)] [General impression: effecient,weak... ] ")
    amount = context.args[0]
    description = context.args[1]
    conn = await connect_db()
    await conn.execute("INSERT INTO study(user_id, amount, description) VALUES ($1, $2, $3)", user_id, amount, description)
    await context.reply_text("Study data saved to the database...")
async def show_study(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = await connect_db()
    study_rows = await conn.fetch(
        """
        SELECT DATE(date) AS day, amount
        FROM study
        WHERE user_id = $1
        ORDER BY date ASC
        """,
        user_id,
    )
    study_days = [row["day"] for row in study_rows]
    study_amount = [float(row["amount"]) for row in study_rows]
    fig, ax = plt.subplots()
    ax.plot(study_days, study_amount, marker="o", linestyle="-", linewidth=2)
    ax.set_title("Study tracking graph")
    ax.set_xlabel("Day")
    ax.set_ylabel("Study hours")
    ax.grid(True, linestyle="--", alpha=0.5)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    await context.bot.send_photo(chat_id=user_id, photo=buf, caption="Here's your study report for the last days")
    plt.close(fig)
async def broadcast(update:Update, context:ContextTypes.DEFAULT_TYPE):
    conn = await connect_db()
    rows =  await conn.fetch("SELECT user_id from verified_users")
    user_ids = [row["user_id"] for row in rows]
    user_id = update.effective_user.id
    message = "File uploading (New Courses, TD's and Exams) will take place once the academic year starts, you will be able to use AI on any file uploaded in the database; like you can ask the AI to summarize a peace of content or help you understand a TD's solution; in this matter please consider avoiding huge files when using /askai, it may crash or give unwanted outputs.\nIf any of this is unclear you can contact me via email."
    for chat_id in user_ids:
        try:
            await context.bot.send_message(chat_id,message)
            print("Message sent!")
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
            
from newsapi import NewsApiClient
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the five most recent technology‑related articles."""
    chat_id = update.effective_user.id

    # News API client is synchronous – fine for a short request
    api = NewsApiClient(api_key="2cba450c5bea425aa649f4c4ec5c6a58")
    tech_news = api.get_everything(
        q="technology OR computer science OR engineering",
        language="en",
        sort_by="publishedAt",
        page_size=5,
    )

    for i, article in enumerate(tech_news["articles"], start=1):
        # Guard against missing image URLs
        photo = article.get("urlToImage")
        if not photo:
            continue  # skip articles without an image

        caption = f"{i}. {article['title']} ({article['source']['name']})\n{article.get('description', '')}"
        # `send_photo` is an async method – use await
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)

        # Optional logging for debugging
        print(article)
import aiohttp
ARXIV_API = "http://export.arxiv.org/api/query?search_query=all:{}&start=0&max_results=3"
async def arxiv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /arxiv <keyword>")
        return

    query = " ".join(context.args)
    url = ARXIV_API.format(query)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()

        # arXiv returns Atom XML, we'll parse manually (lightweight)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(data)

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        if not entries:
            await update.message.reply_text("No papers found for that query.")
            return

        reply = f"📑 *Latest arXiv papers on* `{query}`:\n\n"
        for entry in entries:
            title = entry.find("atom:title", ns).text.strip()
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            link = entry.find("atom:id", ns).text.strip()
            authors = [a.text for a in entry.findall("atom:author/atom:name", ns)]
            author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")

            reply += f"🔹 *{title}*\n👤 {author_str}\n📄 {link}\n📝 {summary[:300]}...\n\n"

        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error fetching papers: {e}")

def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    # handlers inserting
    app.add_handler(CommandHandler('start',start))
    app.add_handler(CommandHandler('upload',upload))
    app.add_handler(CommandHandler('get',get_files))
    app.add_handler(MessageHandler(filters.Document.ALL,handle_document))
    app.add_handler(CommandHandler('help',help_command))
    app.add_handler(CommandHandler('delete',delete_file))
    app.add_handler(CommandHandler('search',search_command))
    app.add_handler(CommandHandler('credits',credits_command))
    app.add_handler(CommandHandler('admin', admin_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('done', done_command))
    app.add_handler(conv_handler)
    app.post_init = start_scheduler
    app.add_handler(CommandHandler("askai", askai))
    app.add_handler(CommandHandler('add_expense',add_expense))
    app.add_handler(CommandHandler('summary', summary))
    app.add_handler(CommandHandler('show_chart',show_chart))
    app.add_handler(CommandHandler('add_sleep', add_sleep))
    app.add_handler(CommandHandler('add_sport', add_sport))
    app.add_handler(CommandHandler('show_sleep', show_sleep))
    app.add_handler(CommandHandler('add_study', add_study))
    app.add_handler(CommandHandler('show_sport', show_sport))
    app.add_handler(CommandHandler('broadcast', broadcast))
    app.add_handler(CommandHandler('news', news))
    app.add_handler(CommandHandler('arxiv', arxiv_command))
    app.add_handler(CommandHandler('show_study', show_study))
    print('Bot is running...')
    app.run_polling()
import threading
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    main()
