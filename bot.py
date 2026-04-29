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
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_sender_name(user):
    if not user:
        return "Неизвестный"
    
    # Для анонимных админов
    if user.first_name == "Group" and user.last_name is None:
        return "Анонимный администратор"
    
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not name:
        name = user.username or "Пользователь"
    if user.username:
        return f"{name} (@{user.username})"
    return name

def get_reply_info(message):
    """Получает информацию об ответе, если он есть"""
    if not message.reply_to_message:
        return ""
    
    original = message.reply_to_message
    original_sender = get_sender_name(original.from_user)
    current_sender = get_sender_name(message.from_user)
    
    # Проверяем, не ответил ли пользователь сам себе
    if message.from_user.id == original.from_user.id:
        return ""
    
    return f"📨 {current_sender} ответил {original_sender}\n\n"

# === ТЕКСТОВЫЕ СООБЩЕНИЯ ===
@bot.message_handler(func=lambda m: m.chat.id in [CHAT_A, CHAT_B] and m.text and not m.text.startswith('/'))
def handle_text(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name}\n\n{message.text}", 
                        message_thread_id=thread_id)
        logger.info(f"✅ Текст A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name}\n\n{message.text}")
        logger.info(f"✅ Текст B→A")

# === ФОТО ===
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_photo(CHAT_B, message.photo[-1].file_id, caption=caption, 
                      message_thread_id=thread_id)
        logger.info(f"✅ Фото A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_photo(CHAT_A, message.photo[-1].file_id, caption=caption)
        logger.info(f"✅ Фото B→A")

# === ВИДЕО ===
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_video(CHAT_B, message.video.file_id, caption=caption,
                      message_thread_id=thread_id)
        logger.info(f"✅ Видео A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_video(CHAT_A, message.video.file_id, caption=caption)
        logger.info(f"✅ Видео B→A")

# === GIF (АНИМАЦИЯ) ===
@bot.message_handler(content_types=['animation'])
def handle_animation(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_animation(CHAT_B, message.animation.file_id, caption=caption,
                          message_thread_id=thread_id)
        logger.info(f"✅ GIF A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_animation(CHAT_A, message.animation.file_id, caption=caption)
        logger.info(f"✅ GIF B→A")

# === ДОКУМЕНТЫ ===
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    is_gif = message.document.mime_type == "image/gif"
    
    reply_info = get_reply_info(message)
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        
        if is_gif:
            bot.send_animation(CHAT_B, message.document.file_id, caption=caption,
                              message_thread_id=thread_id)
            logger.info(f"✅ GIF (документ) A→B")
        else:
            bot.send_document(CHAT_B, message.document.file_id, caption=caption,
                             message_thread_id=thread_id)
            logger.info(f"✅ Документ A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        
        if is_gif:
            bot.send_animation(CHAT_A, message.document.file_id, caption=caption)
            logger.info(f"✅ GIF (документ) B→A")
        else:
            bot.send_document(CHAT_A, message.document.file_id, caption=caption)
            logger.info(f"✅ Документ B→A")

# === ГОЛОСОВЫЕ ===
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_voice(CHAT_B, message.voice.file_id,
                      message_thread_id=thread_id)
        bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (голосовое)",
                        message_thread_id=thread_id)
        logger.info(f"✅ Голос A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_voice(CHAT_A, message.voice.file_id)
        bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (голосовое)")
        logger.info(f"✅ Голос B→A")

# === СТИКЕРЫ ===
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_sticker(CHAT_B, message.sticker.file_id,
                        message_thread_id=thread_id)
        bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (стикер)",
                        message_thread_id=thread_id)
        logger.info(f"✅ Стикер A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_sticker(CHAT_A, message.sticker.file_id)
        bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (стикер)")
        logger.info(f"✅ Стикер B→A")

# === АУДИО ===
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    caption = f"{reply_info}📩 {sender_name}"
    if message.caption:
        caption += f"\n\n{message.caption}"
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_audio(CHAT_B, message.audio.file_id, caption=caption,
                      message_thread_id=thread_id)
        logger.info(f"✅ Аудио A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_audio(CHAT_A, message.audio.file_id, caption=caption)
        logger.info(f"✅ Аудио B→A")

# === ВИДЕОСООБЩЕНИЯ ===
@bot.message_handler(content_types=['video_note'])
def handle_video_note(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    if message.chat.id not in [CHAT_A, CHAT_B]:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    reply_info = get_reply_info(message)
    
    if chat_id == CHAT_A:
        thread_id = CHAT_B_THREAD if CHAT_B_THREAD else None
        bot.send_video_note(CHAT_B, message.video_note.file_id,
                          message_thread_id=thread_id)
        bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (видеосообщение)",
                        message_thread_id=thread_id)
        logger.info(f"✅ Видеосообщение A→B")
        
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        bot.send_video_note(CHAT_A, message.video_note.file_id)
        bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (видеосообщение)")
        logger.info(f"✅ Видеосообщение B→A")

# === РЕАКЦИИ НА ПОСТЫ В КАНАЛАХ (РАБОЧАЯ ВЕРСИЯ ИЗ ПРИМЕРА) ===
REACTION_CHANNELS = [-1002185590715, -1001317416582]

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
                requests.get(f"{RENDER_URL}", timeout=10)
                logger.info("🏓 Пинг")
        except:
            pass

if RENDER_URL:
    threading.Thread(target=keep_alive, daemon=True).start()

# === ЗАПУСК С РАБОЧИМИ РЕАКЦИЯМИ ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        
        # Реакции на каналы (как в рабочем примере)
        if update and "channel_post" in update:
            post = update["channel_post"]
            channel_id = post["chat"]["id"]
            if channel_id in REACTION_CHANNELS:
                message_id = post["message_id"]
                url = f"{API_URL}/setMessageReaction"
                data = {"chat_id": channel_id, "message_id": message_id, "reaction": [{"type": "emoji", "emoji": "🔥"}]}
                requests.post(url, json=data, timeout=5)
                logger.info(f"🔥 Реакция на пост {message_id} в канале {channel_id}")
        
        # Обработка остальных обновлений
        update_obj = types.Update.de_json(update)
        bot.process_new_updates([update_obj])
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "OK", 200

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # Удаляем старый вебхук и устанавливаем новый
    bot.remove_webhook()
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook: {webhook_url}")
    
    logger.info("🤖 БОТ ЗАПУЩЕН")
    logger.info(f"Чат A: {CHAT_A}, Чат B: {CHAT_B}, Топик: {CHAT_B_THREAD if CHAT_B_THREAD else 'нет'}")
    logger.info(f"🔥 Реакции на каналы: {REACTION_CHANNELS}")
    
    app.run(host="0.0.0.0", port=port)
