import json 
import asyncpg
import os
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler,
    ContextTypes, filters
)
from datetime import datetime, time
import sys
now = datetime.now().time()
if not (time(8,0) <= now <= time(23,7,59)):
    print(" Bot inactive , Runs only between 8AM and 12AM")

    sys.exit()
def load_token_file(path="token.txt"):
    with open(path,"r") as file:
        return file.read().strip()
API_TOKEN=load_token_file()

def load_admins_file(path="admins.txt"):
    with open(path,"r") as file:
        return [int(line.strip()) for line in file if line.strip().isdigit()]

ADMIN_ID=load_admins_file()
if ADMIN_ID:
    print("ADMINS IDs loaded:", ADMIN_ID)
JSON_PATH = 'data/materiales.json'
upload_state = {}
def get_base(path="databaseurl.txt"):
    with open(path,"r") as f:
        return f.read().strip()
DATABASE_URL = get_base() # Make sure it's set in Railway
if DATABASE_URL:
    print("url:", DATABASE_URL)
async def connect_db():
    return await asyncpg.connect(DATABASE_URL)

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
        DELETE FROM materials WHERE file_name = $1
    """, file_name)
    await conn.close()
    return result

async def find_material_by_filename(file_name):
    conn = await connect_db()
    row = await conn.fetchrow("""
        SELECT * FROM materials WHERE file_name = $1
    """, file_name)
    await conn.close()
    return row

#initial start command
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text( "WELCOME to the Course Material Bot type /help to see available features")
# for upload command always use async 
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return await update.message.reply_text('You are not authorized to upload, get a promotion or get used to it :)')
    
    if len(context.args) != 2:
        return await update.message.reply_text("Wrong sytanx :( , usage: /upload <module> <category> ")

    module,category = context.args
    upload_state[update.effective_user.id] = (module,category)
    await update.message.reply_text(f"Upload target set to :  {module} > {category}\nNow send me the file!")

# for get file command again we use async
async def get_files(update: Update, context:ContextTypes.DEFAULT_TYPE):
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
    # only admins can upload : 
    if user_id not in  ADMIN_ID:
        await update.message.reply_text("Only the admins can play with files :)  respect yourself !!!!")
        return 
    if user_id not in upload_state:
        await update.message.reply_text("Use upload <module> <type> first.")
        return
    document = update.message.document
    if not document:
        await update.message.reply_text("No document found in the message.....")
        return
    module,category = upload_state[user_id]
    file_id = document.file_id
    file_name = document.file_name or f"file_{file_id[:6]}"
    await save_material(module, category, file_name, file_id)

    await update.message.reply_text(f"File Saved!\nModule:{module}\nType: {category}\nName:{file_name}")
    # clean and update
    await update.message.reply_text(f"File saved!\nModule: {module}\nType:{category}\nName:{file_name}")   
    del upload_state[user_id]
async def help_command(update:Update, context = ContextTypes.DEFAULT_TYPE):
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
async def delete_file(update:Update, context = ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return await update.message.reply_text("You are not authorized to delete files")
    if not context.args:
        return await update.message.reply_text("Usage: /delete <filename>")
    filename = " ".join(context.args).strip()
    deleted = await delete_material_by_filename(file_name)
    if deleted:
        await update.message.reply_text(f"File `{file_name}` deleted !!!")
    else:
        await update.message.reply_text(f"No file named `{file_name}` found.")
async def search_command(update:Update, context=ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(" Usage: /search <keyword>")
    keyword = " ".join(context.args).lower()
    matches = await delete_material_by_filename()
    if not matches:
        update.message.reply_text(f"No files found for `{keyword}`")
        
    response = f"*Found {len(matches)} file(s):*\n\n"
    for row in matches:
        response += f"📁{row['module']} --> 📘{row['category']} -->📄{row['category']}"

    await update.message.reply_text(response, parse_mode="Markdown")    

async def credits_command(update:Update, context=ContextTypes.DEFAULT_TYPE):
            
    crrds = """
        *Bot Credits*
        \\-see more projects on my Github \: https\:\/\/github\\.com/AlaFadeli"
        \\-Contact me via email \:  ala\_eddine\\.fadeli@g\\.enp\\.edu\\.dz"
        \\-report an issue \: enpcourse\\.bot@gmail\\.com"
        \\-project launch date \: 2025\\-07\\-19" """

    await update.message.reply_text(crrds, parse_mode='MarkdownV2')

async def admin_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print("Your ID:", user_id)
    print("Admin list", ADMIN_ID)
    if user_id not in ADMIN_ID:
        await update.message.reply_text("You are not authorized to view admin list")    
    return await update.message.reply_text(" You are  authorized, admin")    

async def list_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    materials = load_materials()
    message_lines = ["*Uploaded Materials\:*"]
    for module,category in materials.items():
        for category, files in category.items():
            for filename in files :
                if not filename:
                    await update.message.reply_text("No files available")
                line = f" {module} -- {category} -- {filename}"
                message_lines.append(line,start=1)
    message = "\n".join(message_lines)
    await update.message.reply_text(message, parse_mode="MarkdownV2")

async def done_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in upload_state:
        del upload_state[user_id]
        await update.message.reply_text("Upload session ended.")
    else:
        await update.message.reply_text("No active upload  session")
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
    print('Bot is running...')
    app.run_polling()


if __name__ == "__main__":
    main()
