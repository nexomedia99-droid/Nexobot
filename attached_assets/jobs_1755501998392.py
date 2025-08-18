from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from decorators import admin_only
from db import add_job, get_all_jobs, get_job_by_id, add_applicant, get_applicants_by_job, get_user_by_id, add_badge_to_user, has_badge, get_total_applies
from datetime import datetime
# ======== CONFIG ========
GROUP_ID = -1002777157241
BUZZER_TOPIC_ID = 2
INFLUENCER_TOPIC_ID = 3
PAYMENT_TOPIC_ID = 11

# ======== POST JOB ========
POSTJOB_TITLE, POSTJOB_FEE, POSTJOB_DESC, POSTJOB_TOPIC = range(4)
@admin_only
async def postjob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Masukkan judul job:")
    return POSTJOB_TITLE

async def postjob_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['postjob_title'] = update.message.text.strip()
    await update.message.reply_text("💰 Masukkan fee/job (angka saja):")
    return POSTJOB_FEE

async def postjob_fee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['postjob_fee'] = update.message.text.strip()
    await update.message.reply_text(
        "📋 Masukkan deskripsi job:"
    )
    return POSTJOB_DESC

async def postjob_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['postjob_desc'] = update.message.text.strip()

    # Setelah deskripsi langsung tampilkan tombol topik
    keyboard = [
        [
            InlineKeyboardButton("🎯 Buzzer", callback_data="topic_buzzer"),
            InlineKeyboardButton("🌟 Influencer", callback_data="topic_influencer")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📍 *Mau di posting di mana?:*\n\n"
        "🎯 **Buzzer** - Untuk job buzzer/promosi umum\n"
        "🌟 **Influencer** - Untuk job khusus influencer",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return POSTJOB_TOPIC

async def postjob_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Get stored data
    title = context.user_data['postjob_title']
    fee = context.user_data['postjob_fee']
    desc = context.user_data['postjob_desc'].strip()
    
    # Determine topic based on selection
    if query.data == "topic_buzzer":
        topic_id = BUZZER_TOPIC_ID
        topic_name = "Buzzer"
        topic_emoji = "🎯"
    elif query.data == "topic_influencer":
        topic_id = INFLUENCER_TOPIC_ID
        topic_name = "Influencer"
        topic_emoji = "🌟"
    else:
        await query.edit_message_text("❌ Pilihan tidak valid.")
        return ConversationHandler.END
    
    # Create job in database
    job_id = add_job(title, fee, desc, status="aktif")
    
    # Create job post message
    job_text = (
        f"📢 *JOB BARU - {topic_emoji} {topic_name.upper()}*\n\n"
        f"🆔 ID: {job_id}\n"
        f"📌 {title}\n"
        f"💰 Fee: {fee}\n\n"
        f"{desc}\n\n"
        f"Status: *Aktif*"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Apply Job", callback_data=f"apply_{job_id}")]
    ])
    
    # Send to appropriate topic
    target_chat_id = GROUP_ID or update.effective_chat.id
    send_kwargs = {
        "chat_id": target_chat_id,
        "text": job_text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup,
        "message_thread_id": topic_id
    }
    
    await context.bot.send_message(**send_kwargs)
    
    # Confirm to admin
    await query.edit_message_text(
        f"✅ Job {job_id} berhasil diposting ke topik *{topic_name}* ({topic_emoji})",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END

async def postjob_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Posting job dibatalkan.")
    return ConversationHandler.END

# DAFTARKAN DI MAIN.PY
postjob_conv = ConversationHandler(
    entry_points=[CommandHandler("postjob", postjob_command)],
    states={
        POSTJOB_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, postjob_title)],
        POSTJOB_FEE: [MessageHandler(filters.TEXT & ~filters.COMMAND, postjob_fee)],
        POSTJOB_DESC: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, postjob_desc),
            CommandHandler("done", postjob_desc),
        ],
        POSTJOB_TOPIC: [CallbackQueryHandler(postjob_topic_selection, pattern="^topic_(buzzer|influencer)$")],
    },
    fallbacks=[CommandHandler("cancel", postjob_cancel)],
)

# ======== UPDATE JOB ========
@admin_only
async def updatejob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Gunakan: /updatejob <ID> <aktif/close/cair>")
        return

    job_id, status = context.args[0], context.args[1].lower()
    job = get_job_by_id(job_id)
    if not job:
        await update.message.reply_text("❌ Job tidak ditemukan.")
        return

    if status not in ["aktif", "close", "cair"]:
        await update.message.reply_text("❌ Status hanya: aktif, close, cair.")
        return

    # Update status di DB
    from db import get_conn
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
        conn.commit()

    await update.message.reply_text(
        f"✅ Job {job_id} diperbarui ke status *{status}*", parse_mode="Markdown"
    )

    if status == "cair":
        notif = f"💸 Job {job_id} sudah *CAIR*! Selamat buat semua pelamar 🎉"
        target_chat_id = GROUP_ID or update.effective_chat.id
        send_kwargs = {"chat_id": target_chat_id, "text": notif, "parse_mode": "Markdown"}
        if PAYMENT_TOPIC_ID:
            send_kwargs["message_thread_id"] = PAYMENT_TOPIC_ID
        await context.bot.send_message(**send_kwargs)

@admin_only
async def resetjob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /resetjob all atau /resetjob <ID>")
        return

    arg = context.args[0]
    from db import get_conn
    with get_conn() as conn:
        cur = conn.cursor()
        if arg == "all":
            cur.execute("DELETE FROM jobs")
            cur.execute("DELETE FROM applicants")
            conn.commit()
            await update.message.reply_text("✅ Semua job dihapus.")
        else:
            cur.execute("DELETE FROM jobs WHERE id = ?", (arg,))
            cur.execute("DELETE FROM applicants WHERE job_id = ?", (arg,))
            conn.commit()
            await update.message.reply_text(f"✅ Job {arg} dihapus.")

@admin_only
async def pelamarjob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /pelamarjob <ID>")
        return

    job_id = context.args[0]
    job = get_job_by_id(job_id)
    if not job:
        await update.message.reply_text("❌ Job tidak ditemukan.")
        return

    applicants = get_applicants_by_job(job_id)
    if not applicants:
        await update.message.reply_text("Belum ada pelamar.")
        return

    lines = [f"👥 Pelamar Job {job_id}:"]
    for i, uid in enumerate(applicants, start=1):
        user = get_user_by_id(uid)
        username = user.get("username", f"User {uid}") if user else f"User {uid}"
        lines.append(f"{i}. {username}")

    await update.message.reply_text("\n".join(lines))

# ======== LIST JOB ========
async def listjob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = get_all_jobs()
    if not jobs:
        await update.message.reply_text("😅 Belum ada job tersedia.")
        return

    lines = ["📋 *Daftar Job*:\n"]
    for job in jobs:
        lines.append(f"🆔 {job['id']} | {job['title']} | Status: {job['status']}")
    lines.append("\n_Gunakan_ `/infojob <id>` _untuk melihat detail dan apply pekerjaan._\n _Contoh:_ `/infojob 1`")
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown"
    )

#========= INFO JOB ========
async def infojob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /infojob <ID>")
        return

    job_id = context.args[0]
    job = get_job_by_id(job_id)
    if not job:
        await update.message.reply_text("❌ Job tidak ditemukan.")
        return

    job_text = (
        f"🆔 {job['id']}\n"
        f"📌 {job['title']}\n"
        f"💰 Fee: {job['fee']}\n\n"
        f"{job['desc']}\n\n"
        f"Status: *{job['status']}*"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Apply Job", callback_data=f"apply_{job_id}")]
    ])
    await update.message.reply_text(job_text, parse_mode="Markdown", reply_markup=reply_markup)

# ======== APPLY BUTTON ========
async def apply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Ini tetap untuk feedback "loading" di UI

    user_id = str(query.from_user.id)
    from db import get_user_by_id
    if not get_user_by_id(user_id):
        # Balas di private saja, biar tidak spam grup
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Kamu belum terdaftar! Gunakan /register dulu."
            )
        except:
            pass  # User belum pernah chat bot privat
        return

    job_id = query.data.split("_")[1]
    job = get_job_by_id(job_id)
    if not job:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Job tidak ditemukan."
            )
        except:
            pass
        return

    applicants = get_applicants_by_job(job_id)
    if user_id in applicants:
        # Sudah apply → info di private saja
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Kamu sudah apply job ini."
            )
        except:
            pass
        return

    # Tambah pelamar baru
    add_applicant(job_id, user_id)
    
    # Cek achievement: Member Aktif (10 apply)
    total_apply = get_total_applies(user_id)
    if total_apply >= 10 and not has_badge(user_id, "🎯 Member Aktif"):
        add_badge_to_user (user_id, "🎯 Member Aktif")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 Selamat! Kamu mendapatkan badge baru: *🎯 Member Aktif*",
                parse_mode="Markdown"
            )
        except:
            pass
    # 💼 Worker Pro (50 apply)
    if total_apply >= 50 and not has_badge(user_id, "💼 Worker Pro"):
        add_badge_to_user (user_id, "💼 Worker Pro")
        await context.bot.send_message(chat_id=user_id,
            text="🏆 Hebat! Kamu sekarang *💼 Worker Pro* (50 job berhasil apply)!",
            parse_mode="Markdown")

    # 🚀 Rising Star (1 apply pertama)
    if total_apply == 1 and not has_badge(user_id, "🚀 Rising Star"):
        add_badge_to_user (user_id, "🚀 Rising Star")
        await context.bot.send_message(chat_id=user_id,
            text="🚀 Selamat! Kamu mendapatkan badge *Rising Star* karena apply job pertama kali!",
                parse_mode="Markdown")

    # 🔥 Fast Responder (apply < 5 menit)
    job = get_job_by_id(job_id)  # pastikan fungsi ini ada
    if job and "created_at" in job:
        job_time = datetime.fromisoformat(job["created_at"])
        now = datetime.utcnow()
        delta_minutes = (now - job_time).total_seconds() / 60

        if delta_minutes <= 5 and not has_badge(user_id, "🔥 Fast Responder"):
            add_badge_to_user (user_id, "🔥 Fast Responder")
            await context.bot.send_message(chat_id=user_id,
                text="🔥 Cepat banget! Kamu dapat badge *Fast Responder* karena apply < 5 menit setelah job diposting!",
                parse_mode="Markdown")

        
    # Berikan 2 poin untuk apply job
    from db import add_points_to_user
    add_points_to_user(user_id, 2)
    
    applicants = get_applicants_by_job(job_id)  # refresh setelah ditambah

    # Ambil semua username pelamar
    lines = []
    for i, uid in enumerate(applicants, start=1):
        user = get_user_by_id(uid)
        username = user.get("username", f"User {uid}") if user else f"User {uid}"
        lines.append(f"{i}. {username}")

    posisi = applicants.index(user_id) + 1  # urutan pelamar ke-berapa

    msg = (
        f"✅ Kamu adalah pelamar ke-{posisi}!\nSelamat mengerjakan!\n\n"
        f"📋 *Daftar Pelamar Job {job_id}:*\n"
        + "\n".join(lines)
    )

    # Kirim hanya di privat!
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=msg,
            parse_mode="Markdown"
        )
    except:
        pass  # User belum pernah chat bot privat

    # Tidak mengirim apapun di grup!

# ======== REGISTER HANDLERS ========
#def register_jobs_handlers(application):
