from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ai import start_ai_chat
from db import get_user_by_id

GROUP_LINK = "https://t.me/Nexo_Buzz"  # ganti dengan link grup asli

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🔐 Register Member", callback_data='start_register')],
        [InlineKeyboardButton("🤖 Chat with AI", callback_data='chat_ai')],
        [InlineKeyboardButton("🤝 Kerjasama", callback_data='kerjasama')],
        [InlineKeyboardButton("👤 Member Area", callback_data='member_area')]
        
    ]
    # cek apakah user sudah daftar database
    if get_user_by_id(user_id):
        keyboard.insert(1, [InlineKeyboardButton("👥 Join Group", url=GROUP_LINK)])
    else:
        keyboard.insert(1, [InlineKeyboardButton("👥 Join Group", callback_data='join_group')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "🤖 *Welcome to Nexobot!*\n\n"
        "Aku asisten resmi grup *NexoBuzz* ✨\n\n"
        "💸 Di *NexoBuzz* kamu bisa menghasilkan uang dengan cara jadi "
        "*Buzzer* dan *Influencer*.\n"
        "🔥 Tugasnya simpel: like, komen, follow, report, post, download apk, "
        "ulas apk/maps, campaign, endorse, dan masih banyak lagi!\n\n"
        "Selain itu, kamu juga bisa pakai fitur *AI Assistant* 🤖 buat tanya apa aja.\n\n"
        "Pilih menu di bawah ⬇️"
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Register Member", callback_data='start_register')],
        [InlineKeyboardButton("👥 Join Group", callback_data='join_group')],
        [InlineKeyboardButton("🤖 Chat with AI", callback_data='chat_ai')],
        [InlineKeyboardButton("🤝 Kerjasama", callback_data='kerjasama')],
        [InlineKeyboardButton("👤 Member Area", callback_data='member_area')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 Main Menu:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == 'start_register':
        await query.edit_message_text(
            "🔐 Silakan ketik /register untuk memulai proses pendaftaran interaktif."
        )

    elif query.data == 'join_group':
        if not get_user_by_id(user_id):
            await query.edit_message_text(
                "❌ Harus daftar dulu kalo mau join!\n\n"
                "👉 Yuk isi data diri kamu dulu dengan ketik /register"
            )
        else:
            await query.edit_message_text(
                f"🎉 Mantap! Kamu sudah terdaftar.\n\n"
                f"Ini link untuk join ke grup NexoBuzz:\n{GROUP_LINK}"
            )

    elif query.data == 'chat_ai':
        from ai import start_ai_chat
        await start_ai_chat(update, context)

    elif query.data == 'kerjasama':
        await query.edit_message_text(
            "🤝 *Kerjasama dengan Owner*\n\n"
            "Kami terbuka untuk berbagai bentuk kerjasama, baik campaign, promosi, maupun partnership lainnya. "
            "Silakan hubungi Owner melalui DM Telegram untuk detail lebih lanjut.\n\n"
            "📩 Contact: @owner_username",
            parse_mode="Markdown"
        )

    elif query.data == 'member_area':
        await query.edit_message_text(
            "👤 *Member Area*\n\n"
            "Di sini kamu bisa menemukan informasi penting seputar member:\n"
            "- 📌 Gunakan `/myinfo` untuk melihat data diri kamu\n"
            "- ✏️ Gunakan `/editinfo` untuk mengubah data\n"
            "- 📋 Gunakan `/listjob` untuk melihat daftar job\n"
            "- ℹ️ Gunakan `/infojob <ID>` untuk melihat detail job\n\n"
            "❓ *FAQ*:\n"
            "1. Bagaimana cara daftar? → Klik Register atau ketik /register\n"
            "2. Bagaimana cara apply job? → Klik tombol Apply di postingan job\n"
            "3. Bagaimana cara update data? → Gunakan /editinfo",
            parse_mode="Markdown"
        )


async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        welcome_message = (
            f"🎉 Welcome {member.first_name}!\n\n"
            "👋 Selamat datang di grup *NexoBuzz* ✨\n\n"
            "💸 Di sini kamu bisa jadi *Buzzer* dan *Influencer* buat dapetin penghasilan.\n"
            "🔥 Ada banyak campaign seru: like, komen, follow, endorse, ulas aplikasi, dan masih banyak lagi!\n\n"
            "Jangan lupa daftar dulu pake /register biar bisa ikut campaign ya 🚀"
        )
        await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def hidden_tag_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if message and message.startswith('.'):
        await update.message.delete()
        hidden_content = message[1:].strip()
        if hidden_content:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=hidden_content)