import json 
from flask import Flask
import asyncio
import shlex
import asyncpg
import os
from telegram import Update, Document, Bot
import logging
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>ENP Course Material Bot</title>
    <style>
        :root {
            --main-bg: #ffffff;
            --text-color: #222;
            --card-bg: #f0f4f8;
            --accent: #005dce;
        }

        [data-theme="dark"] {
            --main-bg: #121212;
            --text-color: #ddd;
            --card-bg: #1f1f1f;
            --accent: #3399ff;
        }

        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: var(--main-bg);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
            transition: background 0.3s, color 0.3s;
        }

        .container {
            max-width: 800px;
            background: var(--main-bg);
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 0 20px rgba(0,0,0,0.08);
            text-align: center;
        }

        h1 {
            color: var(--accent);
        }

        .tagline {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }

        .commands {
            text-align: left;
            margin-top: 2rem;
        }

        .commands h2 {
            margin-bottom: 1rem;
        }

        .command-list {
            list-style: none;
            padding: 0;
        }

        .command-list li {
            margin: 0.8rem 0;
            padding: 1rem;
            background: var(--card-bg);
            border-left: 4px solid var(--accent);
            border-radius: 6px;
        }

        .command-list code {
            font-weight: bold;
            color: var(--accent);
            background: rgba(0, 93, 206, 0.1);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
        }

        .button {
            display: inline-block;
            margin-top: 2rem;
            background: var(--accent);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            transition: background 0.3s;
        }

        .button:hover {
            background: #004bb5;
        }

        .credits {
            margin-top: 3rem;
            font-size: 0.9rem;
            color: #888;
        }

        .footer-links {
            margin-top: 1rem;
        }

        .footer-links a {
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
            border-radius: 8px;
            border: 1px solid #ccc;
        }

        @media (max-width: 600px) {
            .container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="theme-toggle" onclick="toggleTheme()">🌙 Toggle Theme</div>
    <div class="container">
        <h1>📚 ENP Course Material Bot</h1>
        <p class="tagline">Your assistant to access, upload, and manage ENP study files directly on Telegram.</p>

        <a class="button" href="https://t.me/ENPcoursebot" target="_blank">🚀 Open @ENPcoursebot on Telegram</a>

        <div class="commands">
            <h2>📖 Bot Commands</h2>
            <ul class="command-list">
                <li><code>/start</code> — Welcome message</li>
                <li><code>/help</code> — Show help menu</li>
<li><code>/upload &lt;module&gt; &lt;category&gt;</code> — Upload a file (admins only)</li>
                <li><code>/done</code> — Reset upload state after you're done</li>
                <li><code>/get &lt;module&gt; &lt;category&gt;</code> — Retrieve saved files</li>
                <li><code>/delete &lt;filename&gt;</code> — Delete file by name (admins only)</li>
                <li><code>/search &lt;keyword&gt;</code> — Search for matching keywords</li>
                <li><code>/credits</code> — Project owner + contact</li>
                <li><code>/register</code> — Regester usig enp email</li>
            </ul>
        </div>

        <div class="credits">
            Made by <strong>Fadeli Ala Eddine</strong> <br />
            Contact: <a href="mailto:enpcoursebot@gmail.com">enpcoursebot@gmail.com</a>
            <div class="footer-links">
                <a href="https://github.com/AlaFadeli" target="_blank">GitHub</a>
                • <a href="https://t.me/ENPcoursebot" target="_blank">Telegram Bot</a>
            </div>
        </div>
    </div>

    <script>
        function toggleTheme() {
            const current = document.documentElement.getAttribute("data-theme");
            const next = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            localStorage.setItem("theme", next);
        }

        // Load saved theme
        const saved = localStorage.getItem("theme") || "light";
        document.documentElement.setAttribute("data-theme", saved);
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
ADMIN1= os.getenv("ADMIN1")
ADMIN2= os.getenv("ADMIN2")
ADMIN3= os.getenv("ADMIN3")
ADMIN4= os.getenv("ADMIN4")
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
⚙️ Type /help to explore tools  
📝 Don’t forget to /register before using commands.""")
# for upload command always use async 
@registered_only
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_user.id not in ADMIN_ID:
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
    return ASK_EMAIL
conv_handler = ConversationHandler(entry_points= [CommandHandler("register", register_command)],
                                states = {
                                    ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
                                    ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_code)],
                                },
                                fallbacks = [],
)
#async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    command = [] 
#
#    await update.message.reply_text(f"Most used command : {command}")


# finaly main func
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
    print('Bot is running...')
    app.run_polling()
import threading
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    main()
