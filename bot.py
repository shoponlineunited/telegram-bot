import nest_asyncio
nest_asyncio.apply()

import os
import random
import json
import datetime
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Token del bot Telegram (inserito manualmente)
TOKEN = "7725405275:AAFlQ8RicJvYPQrAC6Oaru1LEY5BNE7ChPg"
print(f"🔍 Il token caricato è: {TOKEN}")

# 🔹 Assicuriamoci che la cartella "media" esista
MEDIA_FOLDER = "media"
if not os.path.exists(MEDIA_FOLDER):
    print("❌ La cartella 'media' non esiste! La creo adesso.")
    os.makedirs(MEDIA_FOLDER, exist_ok=True)
print("📂 Contenuto della cartella media:", os.listdir(MEDIA_FOLDER))

# File per memorizzare i punti degli utenti
USER_POINTS_FILE = "user_points.json"
try:
    with open(USER_POINTS_FILE, "r") as file:
        user_points = json.load(file)
except FileNotFoundError:
    user_points = {}

# 🔹 Risposte casuali per messaggi
PHOTO_RESPONSES = [
    "🚀 Boom! Questa ti piacerà! 😎",
    "Ecco uno scatto speciale per te! 📸",
    "Guarda questa bellezza! 😍",
    "Wow, che capolavoro! 🎨",
]
VIDEO_RESPONSES = [
    "Goditi questo video! 🎥",
    "Guarda cosa ho trovato per te! 👀",
    "Un video che potrebbe piacerti! 🔥",
]

# ✅ Funzione di avvio
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🎉 Benvenuto nel bot! Invia una foto o un video e riceverai un altro media in cambio!")

# ✅ Funzione per gestire i media ricevuti
async def receive_media(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user_points[user_id] = user_points.get(user_id, 0) + 1
    with open(USER_POINTS_FILE, "w") as file:
        json.dump(user_points, file)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if update.message.photo:
        media_type = "photo"
        received_filename = f"foto_{timestamp}.jpg"
        file_obj = await update.message.photo[-1].get_file()
    elif update.message.video:
        media_type = "video"
        received_filename = f"video_{timestamp}.mp4"
        file_obj = await update.message.video.get_file()
    else:
        await update.message.reply_text("⚠️ Per favore, invia una foto o un video.")
        return
    received_path = os.path.join(MEDIA_FOLDER, received_filename)
    await file_obj.download_to_drive(received_path)
    if user_points[user_id] % 5 == 0:
        await update.message.reply_text("🎉 Complimenti! Hai inviato 5 media e ricevi 3 media in omaggio! 🚀")
        await send_multiple_media(update, 3)
    else:
        await send_random_media(update, media_type)

# ✅ Funzione per inviare un media casuale
async def send_random_media(update: Update, media_type):
    media_files = [f for f in os.listdir(MEDIA_FOLDER) if f.startswith(media_type)]
    if not media_files:
        await update.message.reply_text("😕 Non ho più media da inviarti, riprova più tardi!")
        return
    random_file = random.choice(media_files)
    file_path = os.path.join(MEDIA_FOLDER, random_file)
    with open(file_path, "rb") as media:
        if media_type == "photo":
            await update.message.reply_photo(media, caption=random.choice(PHOTO_RESPONSES))
        else:
            await update.message.reply_video(media, caption=random.choice(VIDEO_RESPONSES))

# ✅ Funzione per inviare 3 media in una volta
async def send_multiple_media(update: Update, count=3):
    media_files = os.listdir(MEDIA_FOLDER)
    if len(media_files) < count:
        await update.message.reply_text("😕 Non abbiamo abbastanza media, riceverai quello che abbiamo!")
        count = len(media_files)
    random_files = random.sample(media_files, count)
    for file_name in random_files:
        file_path = os.path.join(MEDIA_FOLDER, file_name)
        with open(file_path, "rb") as media:
            if file_name.startswith("photo"):
                await update.message.reply_photo(media, caption=random.choice(PHOTO_RESPONSES))
            else:
                await update.message.reply_video(media, caption=random.choice(VIDEO_RESPONSES))

# ✅ Configuriamo l'applicazione Telegram
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, receive_media))

# ✅ Configurazione Webhook per Render
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'default.render.com')}/webhook"

async def start_webhook():
    await app.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook impostato su {WEBHOOK_URL}")
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",
        webhook_url=WEBHOOK_URL
    )

# ✅ Avvio del bot in modalità sincrona (Render gestisce il loop internamente)
if __name__ == "__main__":
    print("🚀 Avvio del bot su Render con Webhook...")
    # Usando app.run_webhook() in modalità sincrona (è bloccante e gestisce internamente il loop)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",
        webhook_url=WEBHOOK_URL
    )
