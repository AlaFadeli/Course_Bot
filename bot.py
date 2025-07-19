import json 
import os
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler,
    ContextTypes, filters
)
API_TOKEN = os.getenv("COURSE_TOKEN")
ADMIN_ID =  os.getenc("ADMIN_ID")

JSON_PATH = 'data/materiales.json'
upload_state = {}

# Bot logic functions


def load_materials():
    if not os.path.exists(JSON_PATH):
        return {}
    with open(JSON_PATH,'r') as f:
        return json.load(f)

def save_materials(data):
    os.makedirs(os.path.dirname(JSON_PATH),exist_ok = True)
    with open(JSON_PATH,'w') as f:
        json.dump(data,f,indent=2)

#def search_files(query:str):
#    materials = load_materials()
#    results = []
#    for module,category in materials.items():
#        if "course" in category:

#initial start command

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text( "WELCOME to the Course Material Bot type /help to see available features")

# for upload command always use async 

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
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
    data = load_materials()

    if module not in data or category not in data[module]:
        return await update.message.reply_text("No files found in this category. !!!")    

    for name, file_id in data[module][category].items():
        await update.message.reply_document(document=file_id, caption=name)
    # as usual for ANY command : async
         
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # only admins can upload : 
    if user_id != ADMIN_ID:
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
    
    data = load_materials()
    if module not in data:
        data[module] = {}
    if category not in data[module]:
        data[module][category] = {}
    
    data[module][category][file_name] = file_id
    save_materials(data)
    # clean and update
    await update.message.reply_text(f"File saved!\nModule: {module}\nType:{category}\nName:{file_name} ")
    
    del upload_state[user_id]

async def help_command(update:Update, context = ContextTypes.DEFAULT_TYPE):
    commands = """
        *ENP Course Material Bot commands:*
        /start -Welcome message
        /help  -show this current help menu
        /upload <module> <category> -Sets target to upload a file (for admins only) 
        /get <module> <category> -Retrieve saved files 
        /delete <filename> -deletes file name (for admins only)
        /search <keyword> -searchs for matching words 
        /credits - project owner + contact
            note: After /upload ,send your file directly.
        """
    await update.message.reply_text(commands, parse_mode="Markdown")

async def delete_file(update:Update, context = ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("You are not authorized to delete files")
    if not context.args:
        return await update.message.reply_text("Usage: /delete <filename>")
    filename = " ".join(context.args).strip()
    materials = load_materials()
    found = False
    for module , category in materials.items():
        if "course" in category  and filename in category["course"]:
            del category["course"][filename]
            return await update.message.reply_text(f"File {filename} deleted !!! ")
            found = True
            break
    if found:
        save_materials(materials)

async def search_command(update:Update, context=ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(" Usage: /search <keyword>")
    keyword = " ".join(context.args).lower()
    materials = load_materials()
    matches = []
    for module,category in materials.items():
        for category, files in category.items():
            for filename in files:
                if keyword in filename.lower():
                    matches.append((module,category,filename))
    if not matches:
        return await update.message.reply_text(f"No files found for '{keyword}'")

    response = f"*Found {len(matches)} file(s):*\n\n"    
    for module,category, filename in matches:
        response += f"📁 {module} | 📘 {category}\n📄 {filename}\n\n"
    await update.message.reply_text(response, parse_mode="Markdown")    

async def credits_command(update:Update, context=ContextTypes.DEFAULT_TYPE):
    credits_= """
        - see more projects on my Github : https://github.com/AlaFadeli
        - Contact me via email :  ala_eddine.fadeli@g.enp.edu.dz
        - report an issue : enpcourse.bot@gmail.com
        - project launch date : 2025-07-19  
            """
    await update.message.reply_text(credits_ ,parse_mode="Markdown")

# finaly main func
def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    # handlers inserting
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('upload', upload))
    app.add_handler(CommandHandler('get', get_files))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('delete',delete_file))
    app.add_handler(CommandHandler('search', search_command))
    app.add_handler(CommandHandler('credits',credits_command))
    print('Bot is running...')
    app.run_polling()


if __name__ == "__main__":
    main()
