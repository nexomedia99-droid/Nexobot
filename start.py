from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_user_by_id
from utils import get_user_display_name

GROUP_LINK = "https://t.me/Nexo_Buzz"
#======= MEMBER AREA MULTI PAGE =======

MEMBER_AREA_PAGES = {
    "member_area_1": (
        "👤 <b>Member Area (1/3)</b>\n\n"
        "🎛️ <b>Commands Tersedia:</b>\n"
        "• <code>/myinfo</code> - Lihat profil kamu\n"
        "• <code>/editinfo</code> - Edit data member\n"
        "• <code>/points</code> - Cek poin kamu\n"
        "• <code>/myreferral</code> - Lihat referral kamu\n\n"
        "💼 <b>Job Commands:</b>\n"
        "• <code>/listjob</code> - Daftar job tersedia\n"
        "• <code>/infojob id job</code> - Detail job tertentu\n"
    ),
    "member_area_2": (
        "👤 <b>Member Area (2/3)</b>\n\n"
        "🏆 <b>Lainnya:</b>\n"
        "• <code>/leaderboard</code> - Papan peringkat\n"
        "• <code>/points</code> - Cek poin kamu\n"
        "• <code>/summary</code> - Ringkasan percakapan grup\n"
        "• <code>/help</code> - Bantuan lengkap\n\n"
        "<code>/startai</code> - Mode interaktif AI\n"
        "🤖 Tanya seputar dunia perbuzzeran: MG, Handle, Talent, dll.\n\n"
        "‼️ <b>PERINGATAN</b>\n"
        "• Jangan bagikan data pribadi\n"
        "• Dilarang promosi, spam, dan curang\n"
    ),
    "member_area_3": (
        "👤 <b>Member Area (3/3)</b>\n\n"
        "🔥 <b>Promote Sosmed</b>\n"
        "Promosi akun kamu dan dapatkan followers serta poin!\n\n"
        "🎯 <b>Promosi Standar</b>\n"
        "• <code>/promote &lt;link&gt;</code>\n"
        "• Aktif 24 jam\n"
        "• Biaya: 10 poin\n\n"
        "🌟 <b>Promosi Spesial</b>\n"
        "• <code>/promote_special &lt;link&gt;</code>\n"
        "• Di-pin selama 3 hari\n"
        "• Biaya: 15 poin\n\n"
        "📊 <b>Analitik</b>\n"
        "• <code>/cek_followers &lt;ID&gt;</code> - Lihat pengklik\n\n"
        "💡 Tips:\n"
        "• Gunakan link valid\n"
        "• Dilarang curang\n"
        "• Lapor ke admin jika ada masalah"
    ),
}


#=========== START COMMAND ===========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = str(update.effective_user.id)
    user_display = get_user_display_name(update.effective_user)

    # Check if user is registered
    is_registered = get_user_by_id(user_id) is not None

    if is_registered:
        welcome_text = (
            f"👋 Halo kembali, <b>{user_display}</b>!\n\n"
            "Apa yang bisa saya bantu hari ini?"
        )
        keyboard = [
            [InlineKeyboardButton("👤 Member Area", callback_data='member_area')],
            [InlineKeyboardButton("👥 Join Group", url=GROUP_LINK)],
            [InlineKeyboardButton("🤖 Chat with AI", callback_data='chat_ai')],
            [InlineKeyboardButton("🤝 Kerjasama", callback_data='menu_kerjasama')],
            [InlineKeyboardButton("💼 Rekber", url="https://t.me/NexorekberBot")],
        ]
    else:
        welcome_text = (
            f"🤖 <b>Welcome to Nexobot, {user_display}!</b>\n\n"
            "Aku asisten resmi grup <b>NexoBuzz</b> ✨\n\n"
            "💸 Di <b>NexoBuzz</b> kamu bisa menghasilkan uang dengan cara jadi "
            "<b>Buzzer</b> dan <b>Influencer</b>.\n"
            "🔥 Tugasnya simpel: like, komen, follow, report, post, download apk, "
            "ulas apk/maps, campaign, endorse, dan masih banyak lagi!\n\n"
            "Selain itu, kamu juga bisa pakai fitur <b>AI Assistant</b> 🤖 buat tanya apa aja.\n\n"
            "Pilih menu di bawah ⬇️"
        )
        keyboard = [
            [InlineKeyboardButton("🔐 Register Member", callback_data='start_register')],
            [InlineKeyboardButton("👥 Join Group", callback_data='join_group')],
            [InlineKeyboardButton("🤖 Chat with AI", callback_data='chat_ai')],
            [InlineKeyboardButton("🤝 Kerjasama", callback_data='menu_kerjasama')],
            [InlineKeyboardButton("💼 Rekber", url="https://t.me/NexorekberBot")],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")


#=========== BUTTON HANDLER ===========
# Perbaikan pada fungsi button_handler

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani callback tombol inline."""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    # ⚠️ Logika sudah diperbaiki: Menggabungkan semua kondisi dengan benar
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
            "🤖 *NexoAi*\n\n"
            "Pilih mode AI yang ingin kamu gunakan:\n\n"
            "🔹 /startai - Mode interaktif (chat langsung)\n"
            "🔹 /ai <pertanyaan> - Tanya sekali langsung\n"
            "🔹 /stopai - Hentikan mode interaktif\n\n"
            "💡 *Tips:* Mode interaktif memungkinkan kamu chat tanpa harus ketik `/ai` setiap kali!",
            parse_mode="Markdown"
        )

    elif query.data == 'menu_kerjasama':
        await query.edit_message_text(
            "🤝 *Kerjasama dengan Owner*\n\n"
            "Kami terbuka untuk berbagai bentuk kerjasama:\n"
            "• 📈 Campaign & Promosi\n"
            "• 🤝 Partnership Bisnis\n"
            "• 💼 Kolaborasi Proyek\n"
            "• 🎯 Jasa Buzzer\n\n"
            "Info Pricelist tanyakan langsung ke admin\n"
            "Untuk membahas kerjasama lebih lanjut, silakan hubungi owner melalui DM Telegram.\n\n"
            "📩 *Contact:* @Nexoitsme",
            parse_mode="Markdown"
        )

    elif query.data.startswith('member_area'):
           user_data = get_user_by_id(user_id)
           if not user_data:
               await query.edit_message_text(
                   "❌ <b>Akses Ditolak</b>\n\n"
                   "Kamu belum terdaftar sebagai member!\n\n"
                   "👉 Ketik /register untuk mendaftar.",
                   parse_mode="HTML"
               )
               return

           page = query.data  # e.g., 'member_area', 'member_area_1', etc.
           if page == "member_area":
               page = "member_area_1"  # default to first page

           text = MEMBER_AREA_PAGES.get(page)
           if not text:
               await query.edit_message_text("❌ Halaman tidak ditemukan.")
               return

           # Navigation buttons
           nav_buttons = []
           if page == "member_area_1":
               nav_buttons = [[InlineKeyboardButton("➡️ Next", callback_data="member_area_2")]]
           elif page == "member_area_2":
               nav_buttons = [
                   [InlineKeyboardButton("⬅️ Back", callback_data="member_area_1"),
                    InlineKeyboardButton("➡️ Next", callback_data="member_area_3")]
               ]
           elif page == "member_area_3":
               nav_buttons = [
                   [InlineKeyboardButton("⬅️ Back", callback_data="member_area_2"),]]

           await query.edit_message_text(
               text,
               parse_mode="HTML",
               reply_markup=InlineKeyboardMarkup(nav_buttons)
           )

#==========MILESTONE CHECK==========
# Mapping milestone → pesan custom
MILESTONE_MESSAGES = {
    20: (
        "🎉 Selamat datang member baru!\n"
        "Sekarang kita sudah berjumlah 20 orang 👥\n"
        "Terima kasih sudah jadi bagian dari keluarga ini 🤝"
    ),
    30: (
        "🎉 Hore! Grup ini sudah mencapai 30 member!\n"
        "Semoga makin rame, makin seru, dan makin bermanfaat 🙌"
    ),
    40: (
        "🎉 Yeay! Sudah ada 40 member di sini!\n"
        "Jangan lupa saling sapa biar makin akrab 🤗"
    ),
    50: (
        "🚀 WOW! Kita sudah 50 member!\n"
        "Makin gede, makin kuat, makin solid 💪"
    ),
    100: (
        "🎉 WOW! Kita sudah 100 member!\n"
        "Terima kasih banyak atas dukungan kalian semua 🙏"
    ),
    200: (
        "🎉 ANJAYY! Udah 200 member cok! Mantap!\n"
        "Makasih semuanya 😭"
    ),
    300: (
        "🎉 WUIIHHH!! 300 member nihh!\n"
        "Mantap pisan euyy...!!!"
    ),
}

DEFAULT_MESSAGE = (
    "🎉 Grup ini sudah mencapai {count} member!\n"
    "Terima kasih sudah gabung 🙌"
)


async def check_milestone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle milestone welcome message (no personal welcome)."""
    chat_id = update.effective_chat.id

    # Cek jumlah member real setelah ada yang join
    member_count = await context.bot.get_chat_member_count(chat_id)

    # Hanya kirim pesan kalau jumlah member kelipatan 10
    if member_count % 10 == 0:
        if member_count in MILESTONE_MESSAGES:
            milestone_msg = MILESTONE_MESSAGES[member_count]
        else:
            milestone_msg = DEFAULT_MESSAGE.format(count=member_count)

        await context.bot.send_message(
            chat_id=chat_id,
            text=milestone_msg
        )

#=====NEW MEMBER HANDLER=====

# Handler untuk member baru
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered when a new member joins"""
    await check_milestone(update, context)


# Handler untuk member keluar
async def left_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered when a member leaves"""
    await check_milestone(update, context)


# ======= HIDDEN TAG HANDLER =======
async def hidden_tag_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hidden tag messages (starting with .)"""
    try:
        message = update.message.text

        if message and message.startswith('.'):
            # Hapus pesan asli
            await update.message.delete()

            # Ambil konten tersembunyi (setelah titik)
            hidden_content = message[1:].strip()

            if hidden_content:
                # Kirim ulang konten tersembunyi
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=hidden_content,
                    parse_mode="Markdown" if any(
                        char in hidden_content for char in ['*', '_', '`']
                    ) else None
                )
    except Exception:
        # Jika gagal hapus (tidak ada hak admin), abaikan
        pass
