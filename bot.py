import os
import logging
import requests
import threading
import time
from flask import Flask, request
from telebot import TeleBot, types

# === ПЕРЕМЕННЫЕ ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_A = int(os.environ.get("CHAT_A", 0))
CHAT_B = int(os.environ.get("CHAT_B", 0))
CHAT_B_THREAD = int(os.environ.get("CHAT_B_THREAD", 0))
RENDER_URL = os.environ.get("RENDER_URL", "")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(BOT_TOKEN)

def get_sender_name(user):
    if not user:
        return "Неизвестный"
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not name:
        name = user.username or "Пользователь"
    if user.username:
        return f"{name} (@{user.username})"
    return name

# === ОТДЕЛЬНЫЕ ХЕНДЛЕРЫ ДЛЯ КАЖДОГО ТИПА ===

# Текст
@bot.message_handler(func=lambda m: m.chat.id in [CHAT_A, CHAT_B] and m.text and not m.text.startswith('/'))
def handle_text(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name}\n\n{message.text}", 
                        message_thread_id=thread_id)
        logger.info(f"✅ Текст из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name}\n\n{message.text}")
        logger.info(f"✅ Текст из B в A")

# Фото
@bot.message_handler(content_types=['photo'], func=lambda m: m.chat.id in [CHAT_A, CHAT_B])
def handle_photo(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_photo(CHAT_B, message.photo[-1].file_id, caption=caption, 
                      message_thread_id=thread_id)
        logger.info(f"✅ ФОТО из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_photo(CHAT_A, message.photo[-1].file_id, caption=caption)
        logger.info(f"✅ ФОТО из B в A")

# Видео
@bot.message_handler(content_types=['video'], func=lambda m: m.chat.id in [CHAT_A, CHAT_B])
def handle_video(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_video(CHAT_B, message.video.file_id, caption=caption,
                      message_thread_id=thread_id)
        logger.info(f"✅ ВИДЕО из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_video(CHAT_A, message.video.file_id, caption=caption)
        logger.info(f"✅ ВИДЕО из B в A")

# GIF (анимация)
@bot.message_handler(content_types=['animation'], func=lambda m: m.chat.id in [CHAT_A, CHAT_B])
def handle_gif(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_animation(CHAT_B, message.animation.file_id, caption=caption,
                          message_thread_id=thread_id)
        logger.info(f"✅ GIF из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_animation(CHAT_A, message.animation.file_id, caption=caption)
        logger.info(f"✅ GIF из B в A")

# Файлы
@bot.message_handler(content_types=['document'], func=lambda m: m.chat.id in [CHAT_A, CHAT_B])
def handle_document(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_document(CHAT_B, message.document.file_id, caption=caption,
                         message_thread_id=thread_id)
        logger.info(f"✅ ФАЙЛ из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_document(CHAT_A, message.document.file_id, caption=caption)
        logger.info(f"✅ ФАЙЛ из B в A")

# Голосовые
@bot.message_handler(content_types=['voice'], func=lambda m: m.chat.id in [CHAT_A, CHAT_B])
def handle_voice(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_voice(CHAT_B, message.voice.file_id,
                      message_thread_id=thread_id)
        bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (голосовое)",
                        message_thread_id=thread_id)
        logger.info(f"✅ ГОЛОС из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_voice(CHAT_A, message.voice.file_id)
        bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (голосовое)")
        logger.info(f"✅ ГОЛОС из B в A")

# Стикеры
@bot.message_handler(content_types=['sticker'], func=lambda m: m.chat.id in [CHAT_A, CHAT_B])
def handle_sticker(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_sticker(CHAT_B, message.sticker.file_id,
                        message_thread_id=thread_id)
        bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (стикер)",
                        message_thread_id=thread_id)
        logger.info(f"✅ СТИКЕР из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_sticker(CHAT_A, message.sticker.file_id)
        bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (стикер)")
        logger.info(f"✅ СТИКЕР из B в A")

# Аудио
@bot.message_handler(content_types=['audio'], func=lambda m: m.chat.id in [CHAT_A, CHAT_B])
def handle_audio(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_audio(CHAT_B, message.audio.file_id, caption=caption,
                      message_thread_id=thread_id)
        logger.info(f"✅ АУДИО из A в B")
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_audio(CHAT_A, message.audio.file_id, caption=caption)
        logger.info(f"✅ АУДИО из B в A")

# === РЕАКЦИИ НА ПОСТЫ В КАНАЛАХ ===
@bot.channel_post_handler(func=lambda m: True)
def channel_reaction(message):
    allowed = [-1001317416582, -1002185590715]
    if message.chat.id not in allowed:
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
        data = {"chat_id": message.chat.id, "message_id": message.message_id, "reaction": [{"type": "emoji", "emoji": "🔥"}]}
        requests.post(url, json=data, timeout=5)
        logger.info(f"🔥 Реакция на пост {message.message_id}")
    except Exception as e:
        logger.error(f"Ошибка реакции: {e}")

# === КОМАНДЫ ===
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "✅ Бот запущен!")

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"Chat ID: {message.chat.id}\nThread ID: {message.message_thread_id}")

# === ПИНГ ===
def keep_alive():
    while True:
        time.sleep(600)
        try:
            if RENDER_URL:
                requests.get(f"{RENDER_URL}")
                logger.info("🏓 Пинг")
        except:
            pass

if RENDER_URL:
    threading.Thread(target=keep_alive, daemon=True).start()

# === ЗАПУСК ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        bot.process_new_updates([types.Update.de_json(update)])
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "OK", 200

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    bot.remove_webhook()
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook: {webhook_url}")
    
    logger.info("🤖 BOT STARTED")
    logger.info(f"Chat A: {CHAT_A}, Chat B: {CHAT_B}, Thread: {CHAT_B_THREAD}")
    
    app.run(host="0.0.0.0", port=port)
