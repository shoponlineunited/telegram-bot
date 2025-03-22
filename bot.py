import os
import random
import json
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Token Telegram (inserito manualmente per evitare problemi su Render)
TOKEN = "7725405275:AAFlQ8RicJvYPQrAC6Oaru1LEY5BNE7ChPg"

# 🔹 Debug: Verifica che il token sia stato caricato correttamente
print(f"🔍 Il token caricato è: {TOKEN}")

# 🔹 Controlliamo se la cartella "media" esiste
if not os.path.exists("media"):
    print("❌ La cartella 'media' non esiste! La creo adesso.")
    os.makedirs("media", exist_ok=True)

# 📂 Stampiamo il contenuto della cartella per debug
print("📂 Contenuto della cartella media:", os.listdir("media"))

# Creazione della cartella "media" se non esiste
MEDIA_FOLDER = "media"
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# Dizionario per memorizzare i punti degli utenti
USER_POINTS_FILE = "user_points.json"

try:
    with open(USER_POINTS_FILE, "r") as file:
        user_points = json.load(file)
except FileNotFoundError:
    user_points = {}

# Risposte casuali per rendere il bot più coinvolgente
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

# Funzione di avvio
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🎉 Benvenuto nel bot! Invia una foto o un video e riceverai un altro media in cambio!")

# Funzione per ricevere media
async def receive_media(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    
    # Controlla se l'utente ha già punti
    user_points[user_id] = user_points.get(user_id, 0) + 1

    # Salva i punti aggiornati nel file
    with open(USER_POINTS_FILE, "w") as file:
        json.dump(user_points, file)

    # Creazione del nome file con data e ora
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if update.message.photo:
        media_type = "photo"
        received_filename = f"foto_{timestamp}.jpg"
        file = await update.message.photo[-1].get_file()

    elif update.message.video:
        media_type = "video"
        received_filename = f"video_{timestamp}.mp4"
        file = await update.message.video.get_file()

    else:
        await update.message.reply_text("⚠️ Per favore, invia una foto o un video.")
        return

    received_path = os.path.join(MEDIA_FOLDER, received_filename)
    await file.download_to_drive(received_path)

    # Se l'utente ha raggiunto 5 invii, riceve 3 media in una sola volta
    if user_points[user_id] % 5 == 0:
        await update.message.reply_text("🎉 Complimenti! Hai inviato 5 media e ricevi 3 media in omaggio! 🚀")
        await send_multiple_media(update, 3)
    else:
        await send_random_media(update, media_type)

# Funzione per inviare un media casuale
async def send_random_media(update: Update, media_type):
    media_files = [f for f in os.listdir(MEDIA_FOLDER) if f.startswith(media_type)]
    
    if not media_files:
        await update.message.reply_text("😕 Non abbiamo più media da inviarti, riprova più tardi!")
        return
    
    random_file = random.choice(media_files)
    file_path = os.path.join(MEDIA_FOLDER, random_file)

    with open(file_path, "rb") as media:
        if media_type == "photo":
            await update.message.reply_photo(media, caption=random.choice(PHOTO_RESPONSES))
        else:
            await update.message.reply_video(media, caption=random.choice(VIDEO_RESPONSES))

# Funzione per inviare 3 media in una sola volta
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

# ✅ Configuriamo l'Applicazione Telegram
app
