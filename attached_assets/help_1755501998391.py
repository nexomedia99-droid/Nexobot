from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = """
*🤖 NexoBot Help Menu*

Selamat datang di *NexoBot*! Berikut adalah daftar fitur yang tersedia:

👤 *Member Commands*
• `/register` — Daftar jadi member (via private chat)
• `/myinfo` — Lihat data diri kamu
• `/editinfo` — Ubah data member

💼 *Job Commands*
• `/listjob` — Lihat daftar job yang tersedia
• `/infojob <ID>` — Lihat detail job tertentu
• *Apply Job*: Klik tombol _Apply Job_ pada postingan job di grup, dan cek DM bot untuk detail pelamar.

🤖 *AI Commands*
• `/ai <pertanyaan>` — Tanya AI di grup (opsional)
• `/startai` — Mulai chat AI (mode interaktif, private chat)
• `/stopai` — Stop mode interaktif AI (private chat)
• `/summary` — Ringkasan obrolan topik (khusus grup)

🔒 *Admin Commands*
• `/listmember` — Lihat daftar member
• `/memberinfo <username1> ... | all` — Lihat info member
• `/paymentinfo <username1> ...` — Lihat info pembayaran member
• `/delete <username1> <username2> ...` — Hapus member dari database
• `/resetpoint <username1> <username2> ...` — Reset poin member ke 0
• `/postjob` — Posting job baru dengan pilihan topik (Buzzer/Influencer)
• `/updatejob <ID> <status>` — Update status job
• `/resetjob all/<ID>` — Hapus job
• `/pelamarjob <ID>` — Lihat daftar pelamar job

ℹ️ *Tips*
- Untuk apply job, pastikan sudah pernah chat bot via private.
- Semua notifikasi pelamar job, akan dikirim lewat private chat bot.

—

_Punya pertanyaan lain? Hubungi admin_
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )