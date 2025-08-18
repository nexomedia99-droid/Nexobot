from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_user_by_id
from utils import get_user_display_name

GROUP_LINK = "https://t.me/Nexo_Buzz"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = str(update.effective_user.id)
    user_display = get_user_display_name(update.effective_user)
    
    # Check if user is registered
    is_registered = get_user_by_id(user_id) is not None
    
    keyboard = [
        [InlineKeyboardButton("🔐 Register Member", callback_data='start_register')],
        [InlineKeyboardButton("🤖 Chat with AI", callback_data='chat_ai')],
        [InlineKeyboardButton("🤝 Kerjasama", callback_data='kerjasama')],
        [InlineKeyboardButton("👤 Member Area", callback_data='member_area')]
    ]
    
    # Add Join Group button based on registration status
    if is_registered:
        keyboard.insert(1, [InlineKeyboardButton("👥 Join Group", url=GROUP_LINK)])
    else:
        keyboard.insert(1, [InlineKeyboardButton("👥 Join Group", callback_data='join_group')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"🤖 *Welcome to Nexobot, {user_display}!*\n\n"
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
    """Menu command handler"""
    user_id = str(update.effective_user.id)
    is_registered = get_user_by_id(user_id) is not None
    
    keyboard = [
        [InlineKeyboardButton("🔐 Register Member", callback_data='start_register')],
        [InlineKeyboardButton("🤖 Chat with AI", callback_data='chat_ai')],
        [InlineKeyboardButton("🤝 Kerjasama", callback_data='kerjasama')],
        [InlineKeyboardButton("👤 Member Area", callback_data='member_area')]
    ]
    
    if is_registered:
        keyboard.insert(1, [InlineKeyboardButton("👥 Join Group", url=GROUP_LINK)])
    else:
        keyboard.insert(1, [InlineKeyboardButton("👥 Join Group", callback_data='join_group')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 *Main Menu:*", reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == 'start_register':
        await query.edit_message_text(
            "🔐 *Pendaftaran Member*\n\n"
            "Untuk memulai proses pendaftaran, silakan ketik:\n"
            "/register\n\n"
            "⚠️ Pastikan kamu melakukan pendaftaran di private chat (DM) ya!",
            parse_mode="Markdown"
        )

    elif query.data == 'join_group':
        if not get_user_by_id(user_id):
            await query.edit_message_text(
                "❌ *Akses Ditolak*\n\n"
                "Kamu harus mendaftar terlebih dahulu sebelum bisa join grup!\n\n"
                "👉 Ketik `/register` untuk memulai pendaftaran.",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"🎉 *Selamat!*\n\n"
                f"Kamu sudah terdaftar sebagai member.\n\n"
                f"Klik link di bawah untuk join grup NexoBuzz:\n{GROUP_LINK}",
                parse_mode="Markdown"
            )

    elif query.data == 'chat_ai':
        await query.edit_message_text(
            "🤖 *AI Assistant*\n\n"
            "Pilih mode AI yang ingin kamu gunakan:\n\n"
            "🔹 `/startai` - Mode interaktif (chat langsung)\n"
            "🔹 `/ai <pertanyaan>` - Tanya sekali langsung\n"
            "🔹 `/stopai` - Hentikan mode interaktif\n\n"
            "💡 *Tips:* Mode interaktif memungkinkan kamu chat tanpa harus ketik `/ai` setiap kali!",
            parse_mode="Markdown"
        )

    elif query.data == 'kerjasama':
        await query.edit_message_text(
            "🤝 *Kerjasama dengan Owner*\n\n"
            "Kami terbuka untuk berbagai bentuk kerjasama:\n"
            "• 📈 Campaign & Promosi\n"
            "• 🤝 Partnership Bisnis\n"
            "• 💼 Kolaborasi Proyek\n"
            "• 🎯 Advertising & Sponsorship\n\n"
            "Untuk membahas kerjasama lebih lanjut, silakan hubungi owner melalui DM Telegram.\n\n"
            "📩 *Contact:* @owner_username",
            parse_mode="Markdown"
        )

    elif query.data == 'member_area':
        user_data = get_user_by_id(user_id)
        if not user_data:
            await query.edit_message_text(
                "❌ *Akses Ditolak*\n\n"
                "Kamu belum terdaftar sebagai member!\n\n"
                "👉 Ketik `/register` untuk mendaftar.",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "👤 *Member Area*\n\n"
                "🎛️ *Commands Tersedia:*\n"
                "• `/myinfo` - Lihat profil kamu\n"
                "• `/editinfo` - Edit data member\n"
                "• `/points` - Cek poin kamu\n"
                "• `/myreferral` - Lihat referral kamu\n\n"
                "💼 *Job Commands:*\n"
                "• `/listjob` - Daftar job tersedia\n"
                "• `/infojob <ID>` - Detail job tertentu\n\n"
                "🏆 *Lainnya:*\n"
                "• `/leaderboard` - Papan peringkat\n"
                "• `/help` - Bantuan lengkap",
                parse_mode="Markdown"
            )

async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new member joining group"""
    for member in update.message.new_chat_members:
        welcome_message = (
            f"🎉 *Welcome {member.first_name}!*\n\n"
            "👋 Selamat datang di grup *NexoBuzz* ✨\n\n"
            "💸 Di sini kamu bisa jadi *Buzzer* dan *Influencer* untuk mendapatkan penghasilan.\n"
            "🔥 Ada banyak campaign seru: like, komen, follow, endorse, review aplikasi, dan masih banyak lagi!\n\n"
            "📝 *Langkah pertama:*\n"
            "1. DM bot dengan ketik `/start`\n"
            "2. Lakukan registrasi dengan `/register`\n"
            "3. Mulai apply job yang tersedia!\n\n"
            "💡 Gunakan `/help` untuk melihat semua fitur yang tersedia.\n\n"
            "Selamat bergabung dan semoga sukses! 🚀"
        )
        await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def hidden_tag_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hidden tag messages (starting with .)"""
    try:
        message = update.message.text
        if message and message.startswith('.'):
            # Delete the original message
            await update.message.delete()
            
            # Extract the hidden content
            hidden_content = message[1:].strip()
            if hidden_content:
                # Send the hidden content
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=hidden_content,
                    parse_mode="Markdown" if any(char in hidden_content for char in ['*', '_', '`']) else None
                )
    except Exception as e:
        # If deletion fails (no admin rights), ignore
        pass
