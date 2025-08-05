import json 
from flask import Flask
import asyncio
import shlex
import asyncpg
import os
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler,ConversationHandler,
    ContextTypes, filters
)
#from secretspy import GMAIL_USER, GMAIL_APP_PASSWORD
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, time
import sys
import random 
import re
from functools import wraps
flask_app= Flask(__name__)
@flask_app.route("/")
def home():
    return "Bot is running"
def run_flask():
    port =int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
def load_token_file(path="token.txt"):
    with open(path,"r") as file:
        return file.read().strip()
API_TOKEN= os.getenv("API_TOKEN")
#def load_admins_file(path="admins.txt"):
#    with open(path,"r") as file:
#        return [int(line.strip()) for line in file if line.strip().isdigit()]
#ADMIN_ID=load_admins_file()
#if ADMIN_ID:
#    print("ADMINS IDs loaded:", ADMIN_ID)
#JSON_PATH = 'data/materiales.json'
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
    print('Bot is running...')
    app.run_polling()
import threading
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    main()
