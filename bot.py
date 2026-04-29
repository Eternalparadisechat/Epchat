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

# === ПЕРЕСЫЛКА СООБЩЕНИЙ МЕЖДУ ЧАТАМИ ===
@bot.message_handler(func=lambda m: m.chat.id in [CHAT_A, CHAT_B] and not (m.text and m.text.startswith('/')))
def relay_messages(message):
    if message.from_user.id == bot.get_me().id:
        return
    
    chat_id = message.chat.id
    sender_name = get_sender_name(message.from_user)
    
    # Формируем информацию об ответе
    reply_info = ""
    if message.reply_to_message:
        original = message.reply_to_message
        original_sender = get_sender_name(original.from_user)
        reply_info = f"📨 {sender_name} ответил(а) {original_sender}\n\n"
    
    # Из чата A в B
    if chat_id == CHAT_A:
        try:
            if message.text:
                bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name}\n\n{message.text}", 
                               message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.photo:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_photo(CHAT_B, message.photo[-1].file_id, caption=caption,
                             message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.video:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_video(CHAT_B, message.video.file_id, caption=caption,
                             message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.document:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_document(CHAT_B, message.document.file_id, caption=caption,
                                message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.animation:  # GIF
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_animation(CHAT_B, message.animation.file_id, caption=caption,
                                 message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.sticker:
                bot.send_sticker(CHAT_B, message.sticker.file_id, 
                               message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
                bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (стикер)",
                               message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.voice:
                # Для голосовых отправляем без caption, потом отдельное сообщение
                bot.send_voice(CHAT_B, message.voice.file_id,
                             message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
                bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (голосовое)",
                               message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.audio:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_audio(CHAT_B, message.audio.file_id, caption=caption,
                             message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            elif message.video_note:  # Кружок
                bot.send_video_note(CHAT_B, message.video_note.file_id,
                                  message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
                bot.send_message(CHAT_B, f"{reply_info}📩 {sender_name} (видеосообщение)",
                               message_thread_id=CHAT_B_THREAD if CHAT_B_THREAD else None)
            logger.info(f"✅ Переслано из A в B: {message.content_type}")
        except Exception as e:
            logger.error(f"Ошибка A→B: {e}")
    
    # Из чата B в A
    elif chat_id == CHAT_B:
        if CHAT_B_THREAD and message.message_thread_id != CHAT_B_THREAD:
            return
        try:
            if message.text:
                bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name}\n\n{message.text}")
            elif message.photo:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_photo(CHAT_A, message.photo[-1].file_id, caption=caption)
            elif message.video:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_video(CHAT_A, message.video.file_id, caption=caption)
            elif message.document:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_document(CHAT_A, message.document.file_id, caption=caption)
            elif message.animation:  # GIF
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_animation(CHAT_A, message.animation.file_id, caption=caption)
            elif message.sticker:
                bot.send_sticker(CHAT_A, message.sticker.file_id)
                bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (стикер)")
            elif message.voice:
                bot.send_voice(CHAT_A, message.voice.file_id)
                bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (голосовое)")
            elif message.audio:
                caption = f"{reply_info}📩 {sender_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                bot.send_audio(CHAT_A, message.audio.file_id, caption=caption)
            elif message.video_note:  # Кружок
                bot.send_video_note(CHAT_A, message.video_note.file_id)
                bot.send_message(CHAT_A, f"{reply_info}📩 {sender_name} (видеосообщение)")
            logger.info(f"✅ Переслано из B в A: {message.content_type}")
        except Exception as e:
            logger.error(f"Ошибка B→A: {e}")

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

# === КОМАНДА /start ===
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "✅ Бот запущен! Пересылаются:\n• Текст\n• Фото\n• Видео\n• GIF\n• Файлы\n• Стикеры\n• Голосовые\n• Аудио\n• Видеосообщения")

# === ПРОСТОЙ ПИНГ ДЛЯ ПРЕДОТВРАЩЕНИЯ ЗАСЫПАНИЯ ===
def keep_alive():
    while True:
        time.sleep(600)  # каждые 10 минут
        try:
            if RENDER_URL:
                requests.get(f"{RENDER_URL}")
                logger.info("🏓 Пинг выполнен")
        except:
            pass

if RENDER_URL:
    threading.Thread(target=keep_alive, daemon=True).start()

# === ЗАПУСК ВЕБХУКА ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        bot.process_new_updates([types.Update.de_json(update)])
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook: {e}")
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
        logger.info(f"✅ Вебхук установлен: {webhook_url}")
    
    logger.info("🤖 БОТ ЗАПУЩЕН")
    logger.info(f"Чат A: {CHAT_A}, Чат B: {CHAT_B}, топик: {CHAT_B_THREAD if CHAT_B_THREAD else 'не используется'}")
    logger.info("✅ Пересылка сообщений включена")
    logger.info("🔥 Реакции на каналы включены")
    
    app.run(host="0.0.0.0", port=port)
