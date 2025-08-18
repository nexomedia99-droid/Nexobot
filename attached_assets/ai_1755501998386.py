import os
import google.generativeai as genai
import traceback
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== PENYIMPAN HISTORY GRUP ==========
# key = (chat_id, thread_id), value = list of messages
group_messages = {}

# ====== Config dari ENV (Replit Secrets) ======
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

if not API_KEY:
    logger.error("❌ ERROR: GEMINI_API_KEY tidak ditemukan di environment variables!")
else:
    logger.info("✅ GEMINI_API_KEY terbaca: %s", API_KEY[:6] + "*****")

# ====== Inisialisasi Gemini ======
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=(
            "Kamu adalah NexoAi: gaya santai, jenaka, Gen Z abiezz, helpful, tidak formal. "
            "Sapa pengguna dengan ramah, pakai emoji secukupnya, jawab ringkas + to the point. "
            "Jangan terlalu kaku, boleh agak bercanda, tapi tetep kasih jawaban bermanfaat."
        ),
    )
    logger.info(f"✅ Gemini model siap: {MODEL_NAME}")
except Exception as e:
    logger.error("❌ Gagal inisialisasi Gemini: %s", e)
    model = None

# ====== Start / Stop AI Chat ======
async def start_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["in_ai_chat"] = True
    intro = (
        "🔥 Yo wassup! Aku *NexoAi* 🤖✨\n\n"
        "Gua siap nemenin ngobrol — tanya apa aja langsung ketik di sini. "
        "Kalo mau selesai, ketik /stopai 🚪\n\n"
        "_Note: Mode ini aktif di chat ini aja._"
    )
    await update.effective_chat.send_message(intro, parse_mode="Markdown")
    logger.info(f"User {update.effective_user.id} started AI chat in chat {update.effective_chat.id}")

async def stop_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["in_ai_chat"] = False
    await update.message.reply_text("👋 Sip, obrolan sama NexoAi ditutup dulu. Jangan lupa balik lagi ya!")
    logger.info(f"User {update.effective_user.id} stopped AI chat in chat {update.effective_chat.id}")

# ====== Chat dengan AI ======
async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Received message: %s", update.message.text)
    if not update.message or not update.message.text:
        return

    chat_type = update.effective_chat.type
    user = update.effective_user
    user_id = user.id if user else "unknown"
    text = update.message.text.strip()

    # === Mode di grup ===
    if chat_type in ("group", "supergroup"):
        if not text.startswith("/ai"):
            return  # ignore semua teks biasa biar gak spam
        user_input = text[3:].strip()
        if not user_input:
            await update.message.reply_text("💡 Gunakan: `/ai <pertanyaan>`", parse_mode="Markdown")
            return
    else:
        # === Mode di private chat ===
        if not context.user_data.get("in_ai_chat"):
            return  # kalau belum start_ai_chat → diam
        user_input = text

    logger.info(f"💬 User [{user_id}] in chat {update.effective_chat.id}: {user_input}")

    if not model:
        await update.message.reply_text("❌ AI belum siap. Cek konfigurasi API key dulu!")
        logger.error(f"User {user_id} tried to use AI when model is not ready.")
        return

    try:
        # Simulasi mengetik
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(1.5)

        response = await asyncio.to_thread(model.generate_content, user_input)
        reply = (response.text or "").strip() if response else "😅 Aku nggak nangkep maksudnya."

        logger.info("🤖 NexoAi response: %s", reply[:120])
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error("❌ Error waktu generate content for user %s: %s", user_id, e, exc_info=True)
        await update.message.reply_text("⚠️ Yah, ada error pas manggil AI. Coba lagi bentar ya.")

# Fungsi untuk memberikan poin aktivitas grup
async def group_activity_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give 2 points for group activity (max once per day per user)"""
    user_id = str(update.effective_user.id)

    # Check if user is registered
    from db import get_user_by_id
    user_data = get_user_by_id(user_id)
    if not user_data:
        return  # User not registered, no points

    # Simple daily limit check using context storage
    today = datetime.now().strftime("%Y-%m-%d")
    daily_points_key = f"daily_points_{user_id}_{today}"

    if not context.bot_data.get(daily_points_key):
        # Give 2 points for group activity
        from db import add_points_to_user
        add_points_to_user(user_id, 2)
        context.bot_data[daily_points_key] = True

# ====== Summary ======
async def save_group_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return

    # Bisa simpan juga di #General (thread_id None)
    thread_id = getattr(update.message, "message_thread_id", None)
    text = (update.message.text or "").strip()
    if not text:
        return

    user = update.effective_user.first_name if update.effective_user else "unknown"
    key = (chat.id, thread_id)

    if key not in group_messages:
        group_messages[key] = []
    group_messages[key].append(f"{user}: {text}")

    # batasi biar ga bengkak
    if len(group_messages[key]) > 50:
        group_messages[key] = group_messages[key][-50:]
    logger.debug(f"Saved message to group history for chat {chat.id}, thread {thread_id}")

    # Call group_activity_points after saving message
    await group_activity_points(update, context)


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❌ Ringkasan hanya bisa dipakai di grup.")
        logger.warning(f"User {update.effective_user.id} tried to use summary command in non-group chat {chat.id}")
        return

    thread_id = getattr(update.message, "message_thread_id", None)
    key = (chat.id, thread_id)
    history = group_messages.get(key, [])

    if not history:
        await update.message.reply_text("😅 Belum ada yang bisa diringkas di topik ini.")
        logger.info(f"No history found for summary in chat {chat.id}, thread {thread_id}")
        return

    history_text = "\n".join(history[-50:])
    prompt = f"Tolong ringkas obrolan ini secara singkat & jelas:\n\n{history_text}"
    user_id = update.effective_user.id if update.effective_user else "unknown"

    logger.info(f"Generating summary for chat {chat.id}, thread {thread_id} requested by user {user_id}")

    try:
        await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
        response = await asyncio.to_thread(model.generate_content, prompt)
        summary = (response.text or "").strip() if response else "😅 Gagal bikin ringkasan."

        await update.message.reply_text(f"📝 Ringkasan obrolan:\n\n{summary}")
        logger.info(f"Successfully generated summary for chat {chat.id}, thread {thread_id}")
    except Exception as e:
        logger.error("❌ Error waktu summary for chat %s, thread %s: %s", chat.id, thread_id, e, exc_info=True)
        await update.message.reply_text("⚠️ Yah, gagal bikin ringkasan. Coba lagi ya.")