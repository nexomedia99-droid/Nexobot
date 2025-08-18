from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = """
🤖 *NexoBot Help Center*

Selamat datang di *NexoBot*! Berikut adalah panduan lengkap fitur yang tersedia:

👤 *MEMBER COMMANDS*
• `/register` — Daftar jadi member (private chat)
• `/myinfo` — Lihat profil dan data diri
• `/editinfo` — Edit data member
• `/points` — Cek poin dan cara mendapatkannya
• `/myreferral` — Info referral dan bonus

💼 *JOB COMMANDS*
• `/listjob` — Daftar semua job tersedia
• `/infojob <ID>` — Detail job tertentu
• *Apply Job* — Klik tombol "Apply Job" di postingan

🤖 *AI ASSISTANT*
• `/ai <pertanyaan>` — Tanya AI (grup)
• `/startai` — Mode chat interaktif (private)
• `/stopai` — Stop mode interaktif
• `/summary` — Ringkasan percakapan grup

🏆 *COMMUNITY*
• `/leaderboard` — Papan peringkat member
• `/help` — Panduan ini

🔒 *ADMIN COMMANDS*
• `/listmember [page]` — Daftar member
• `/memberinfo <username>` — Info detail member
• `/paymentinfo <username>` — Info payment member
• `/delete <username>` — Hapus member
• `/resetpoint <username>` — Reset poin member
• `/addbadge <username> <badge>` — Tambah badge
• `/postjob` — Posting job baru
• `/updatejob <ID> <status>` — Update status job
• `/resetjob <ID>` — Hapus job
• `/pelamarjob <ID>` — Lihat pelamar job

💡 *TIPS & TRIK*
1. **Earning Points:**
   • Apply job: +2 poin
   • Aktif di grup: +1 poin
   • Referral berhasil: +25 poin

2. **Badge System:**
   • 🚀 Rising Star: Apply job pertama
   • 🎯 Member Aktif: 10+ apply
   • 💼 Worker Pro: 50+ apply
   • 🏆 Top Contributor: Peringkat #1

3. **Referral Program:**
   • Bagikan username kamu sebagai kode referral
   • Dapatkan 25 poin setiap referral berhasil
   • User baru dapat bonus 15 poin tambahan

⚠️ *CATATAN PENTING*
• Registrasi dan AI interaktif hanya di private chat
• Apply job memerlukan registrasi terlebih dahulu
• Semua notifikasi job dikirim via private chat
• 1 poin = Rp 10 (informasi saja)

🔗 *DUKUNGAN*
Butuh bantuan? Hubungi admin grup atau gunakan `/ai` untuk pertanyaan umum.

—
*NexoBuzz - Your Gateway to Digital Opportunities* ✨
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show comprehensive help information"""
    try:
        # Check if user wants specific help topic
        if context.args:
            topic = context.args[0].lower()
            
            if topic in ['job', 'jobs']:
                help_text = """
💼 *JOB SYSTEM HELP*

**Cara Apply Job:**
1. Lihat job tersedia: `/listjob`
2. Cek detail: `/infojob <ID>`
3. Klik tombol "Apply Job" di postingan
4. Atau klik tombol di hasil `/infojob`

**Status Job:**
🟢 Aktif - Masih bisa apply
🔴 Close - Sudah ditutup
💸 Cair - Sudah dibayar

**Tips:**
• Apply cepat untuk posisi terdepan
• Baca deskripsi dengan teliti
• Pastikan memenuhi syarat yang diminta
• Tunggu pengumuman dari admin
                """
                
            elif topic in ['ai', 'assistant']:
                help_text = """
🤖 *AI ASSISTANT HELP*

**Mode AI:**
• `/ai <pertanyaan>` - Tanya sekali (grup/private)
• `/startai` - Mode interaktif (private only)
• `/stopai` - Stop mode interaktif

**Fitur AI:**
• Jawab pertanyaan umum
• Bantuan tentang NexoBuzz
• Konsultasi karir digital
• Tips & trik buzzer/influencer

**Group Features:**
• `/summary` - Ringkas percakapan grup
• Otomatis save pesan untuk summary
                """
                
            elif topic in ['point', 'points', 'poin']:
                help_text = """
💰 *POINTS SYSTEM HELP*

**Cara Dapat Poin:**
• Apply job: +2 poin
• Aktif di grup (chat): +1 poin/hari
• Referral berhasil: +25 poin
• Gunakan AI di grup: +1 poin
• Summary grup: +2 poin

**Kegunaan Poin:**
• Ranking di leaderboard
• Badge achievements
• Nilai tukar: 1 poin = Rp 10*

*informasi saja, bukan pembayaran resmi
                """
                
            else:
                help_text = HELP_TEXT
        else:
            help_text = HELP_TEXT
        
        await update.message.reply_text(
            help_text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat menampilkan help. Silakan coba lagi.",
            parse_mode="Markdown"
        )
