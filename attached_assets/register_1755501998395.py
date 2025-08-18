from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters, CommandHandler
)
from db import add_user, get_user_by_id, get_user_by_username, get_all_users, add_points_to_user, get_referrals_by_username, get_badges, add_badge_to_user, has_badge
from datetime import datetime, timedelta, timezone
# State constants
(
    USERNAME, REFERRAL, WHATSAPP, TELEGRAM, PAYMENT_METHOD, PAYMENT_NUMBER, OWNER_NAME,
    CHOOSE_FIELD, EDIT_USERNAME, EDIT_WHATSAPP, EDIT_TELEGRAM, EDIT_PAYMENT_METHOD, EDIT_PAYMENT_NUMBER, EDIT_OWNER_NAME
) = range(14)

# ========== REGISTER ==========

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "❌ Pendaftaran hanya via private chat.\n"
            "Silakan buka DM ke bot lalu kirim /register."
        )
        return ConversationHandler.END

    user_id = str(update.effective_user.id)
    if get_user_by_id(user_id):
        await update.message.reply_text(
            "✅ Kamu sudah terdaftar!\n"
            "Gunakan /editinfo untuk mengubah data."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "✨ Yuk kita mulai proses pendaftaran!\n\n"
        "📌 *Langkah 1/7*\n"
        "👤 *Username*\n"
        "Buat username yang unik! Username akan digunakan untuk pengisian kolom nama pada setiap job. "
        "Akan lebih bagus jika username yang kamu buat sama dengan username akun Telegram kamu!",
        parse_mode="Markdown"
    )
    return USERNAME

async def username_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    if get_user_by_username(username):
        await update.message.reply_text(
            "❌ Username sudah dipakai member lain. Silakan pilih username lain yang unik!"
        )
        return USERNAME
    context.user_data['username'] = username
    await update.message.reply_text(
        "🔗 *Kode Referral (opsional)*\n"
        "Masukkan username teman yang mengajak kamu (atau ketik Skip):",
        parse_mode="Markdown"
    )
    return REFERRAL

async def referral_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ref = update.message.text.strip()
    if ref.casefold() == "skip":
        context.user_data['referrer'] = None
        context.user_data['referrer_user_id'] = None
    else:
        ref_user = get_user_by_username(ref)
        if not ref_user:
            await update.message.reply_text("❌ Kode referral tidak valid. Ketik username teman atau 'Skip'.")
            return REFERRAL
        context.user_data['referrer'] = ref_user['username']  # Simpan username referrer
        context.user_data['referrer_user_id'] = ref_user['user_id']  # Simpan user_id referrer
    await update.message.reply_text(
        "📌 *Langkah 3/7*\n"
        "☎️ *Nomor Whatsapp*\n Masukkan nomor WhatsApp kamu! (08xxx)",
        parse_mode="Markdown"
    )
    return WHATSAPP

async def whatsapp_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['whatsapp'] = update.message.text.strip()
    await update.message.reply_text(
        "📌 *Langkah 4/7*\n"
        "📱 *Nomor Telegram*\n Masukkan nomor Telegram kamu! (08xxx)\n\n"
        "👉 Jika nomor Telegram sama dengan nomor WhatsApp, balas dengan *Skip*",
        parse_mode="Markdown"
    )
    return TELEGRAM

async def telegram_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val.casefold() == "skip":
        context.user_data['telegram'] = context.user_data['whatsapp']
    else:
        context.user_data['telegram'] = val
    keyboard = [
        [
            InlineKeyboardButton("Dana", callback_data="Dana"),
            InlineKeyboardButton("Seabank", callback_data="Seabank")
        ]
    ]
    await update.message.reply_text(
        "📌 *Langkah 5/7*\n"
        "💳 *Metode Payment*\n"
        "Pilih antara Dana atau Seabank",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PAYMENT_METHOD

async def payment_method_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['payment_method'] = query.data
    await query.edit_message_text(
        f"📌 *Langkah 6/7*\n"
        f"🔢 *Nomor Payment*\n Masukkan nomor {query.data} kamu",
        parse_mode="Markdown"
    )
    return PAYMENT_NUMBER

async def payment_number_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['payment_number'] = update.message.text.strip()
    await update.message.reply_text(
        "📌 *Langkah 7/7*\n"
        "📝 *A/n* | Nama Pemilik Rekening/E-Wallet",
        parse_mode="Markdown"
    )
    return OWNER_NAME

async def owner_name_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    context.user_data['owner_name'] = update.message.text.strip()

    # Pastikan data referrer ada di context.user_data sebelum simpan ke database
    referrer_username = context.user_data.get('referrer')
    referrer_user_id = context.user_data.get('referrer_user_id')

    # Simpan user baru ke database
    add_user(user_id, context.user_data)
    data = get_user_by_id(user_id)

    # Proses referral jika ada
    if referrer_user_id:
        # Jika ada referrer, tambahkan ke database dan berikan poin
        context.user_data['referrer'] = referrer_username
        # Berikan 25 poin untuk referrer
        add_points_to_user(referrer_user_id, 25)

        try:
            await context.bot.send_message(
                chat_id=referrer_user_id,
                text=(
                    f"🎉 Selamat! {data['username']} berhasil daftar menggunakan kode referral kamu!\n"
                    f"💰 +25 poin telah ditambahkan ke akun kamu!\n"
                    f"👥 Total referral kamu sekarang: {len(get_referrals_by_username(referrer_username))} orang"
                )
            )
        except Exception:
            pass

    summary = (
        "🎉 *Pendaftaran Berhasil!*\n\n"
        f"👤 Username : `{data['username']}`\n"
        f"☎️ Nomor WhatsApp : `{data['whatsapp']}`\n"
        f"📱 Nomor Telegram : `{data['telegram']}`\n"
        f"💳 Metode Payment : {data['payment_method']}\n"
        f"🔢 Nomor Payment : `{data['payment_number']}`\n"
        f"📝 A/n : {data['owner_name']}\n"
        f"🔗 Direferensi oleh : {data.get('referrer', 'Tidak ada')}\n\n"
        "👉 Gunakan /myinfo untuk melihat data kamu.\n"
        "👉 Gunakan /editinfo untuk mengubah data kamu.\n\n"
        "*Kalau mau join grup klik /start 👉 Join Group*"
    )
    await update.message.reply_text(summary, parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

# ========== EDITINFO ==========

async def editinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = get_user_by_id(user_id)
    if not data:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /register untuk daftar.")
        return ConversationHandler.END
    keyboard = [
        [InlineKeyboardButton("Username", callback_data="edit_username")],
        [InlineKeyboardButton("Whatsapp", callback_data="edit_whatsapp")],
        [InlineKeyboardButton("Telegram", callback_data="edit_telegram")],
        [InlineKeyboardButton("Metode Payment", callback_data="edit_payment_method")],
        [InlineKeyboardButton("Nomor Payment", callback_data="edit_payment_number")],
        [InlineKeyboardButton("A/n (Owner Name)", callback_data="edit_owner_name")],
        [InlineKeyboardButton("Selesai", callback_data="edit_done")],
    ]
    await update.message.reply_text(
        "Mau edit bagian apa?\nPilih salah satu:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSE_FIELD

async def choose_field_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "edit_username":
        await query.edit_message_text("Masukkan username baru:")
        return EDIT_USERNAME
    elif query.data == "edit_whatsapp":
        await query.edit_message_text("Masukkan nomor WhatsApp baru:")
        return EDIT_WHATSAPP
    elif query.data == "edit_telegram":
        await query.edit_message_text("Masukkan nomor Telegram baru:")
        return EDIT_TELEGRAM
    elif query.data == "edit_payment_method":
        keyboard = [
            [InlineKeyboardButton("Dana", callback_data="Dana")],
            [InlineKeyboardButton("Seabank", callback_data="Seabank")]
        ]
        await query.edit_message_text("Pilih metode payment baru:", reply_markup=InlineKeyboardMarkup(keyboard))
        return EDIT_PAYMENT_METHOD
    elif query.data == "edit_payment_number":
        await query.edit_message_text("Masukkan nomor payment baru:")
        return EDIT_PAYMENT_NUMBER
    elif query.data == "edit_owner_name":
        await query.edit_message_text("Masukkan nama pemilik rekening baru:")
        return EDIT_OWNER_NAME
    elif query.data == "edit_done":
        await query.edit_message_text("Edit selesai. Data kamu sudah diupdate.")
        return ConversationHandler.END

async def edit_username_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_val = update.message.text.strip()
    user_id = str(update.effective_user.id)
    # Validasi username unik
    if get_user_by_username(new_val):
        await update.message.reply_text("❌ Username sudah dipakai member lain. Pilih yang lain.")
        return EDIT_USERNAME
    data = get_user_by_id(user_id)
    data['username'] = new_val
    add_user(user_id, data)
    await update.message.reply_text("✅ Username berhasil diubah.")
    return await editinfo_command(update, context)

async def edit_whatsapp_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_val = update.message.text.strip()
    user_id = str(update.effective_user.id)
    data = get_user_by_id(user_id)
    data['whatsapp'] = new_val
    add_user(user_id, data)
    await update.message.reply_text("✅ Nomor WhatsApp berhasil diubah.")
    return await editinfo_command(update, context)

async def edit_telegram_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_val = update.message.text.strip()
    user_id = str(update.effective_user.id)
    data = get_user_by_id(user_id)
    data['telegram'] = new_val
    add_user(user_id, data)
    await update.message.reply_text("✅ Nomor Telegram berhasil diubah.")
    return await editinfo_command(update, context)

async def edit_payment_method_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = get_user_by_id(user_id)
    data['payment_method'] = query.data
    add_user(user_id, data)
    await query.edit_message_text(f"✅ Metode payment diubah ke: {query.data}")
    return await editinfo_command(query, context)

async def edit_payment_number_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_val = update.message.text.strip()
    user_id = str(update.effective_user.id)
    data = get_user_by_id(user_id)
    data['payment_number'] = new_val
    add_user(user_id, data)
    await update.message.reply_text("✅ Nomor Payment berhasil diubah.")
    return await editinfo_command(update, context)

async def edit_owner_name_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_val = update.message.text.strip()
    user_id = str(update.effective_user.id)
    data = get_user_by_id(user_id)
    data['owner_name'] = new_val
    add_user(user_id, data)
    await update.message.reply_text("✅ Nama pemilik rekening berhasil diubah.")
    return await editinfo_command(update, context)

# ========== EXTRA ==========

async def myinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = get_user_by_id(user_id)
    if not data:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /register untuk daftar.")
        return

    points = data.get('points', 0)
    referrer = data.get('referrer', 'Tidak ada')

    badges = get_badges(user_id)
    badge_text = " | ".join(badges) if badges else "Belum ada"
    
    summary = (
        "👤 *Data Member Kamu*\n\n"
        f"👤 Username : `{data['username']}`\n"
        f"🏅 Badge : {badge_text}\n"
        f"📱 Nomor WhatsApp : `{data['whatsapp']}`\n"
        f"💬 Nomor Telegram : `{data['telegram']}`\n"
        f"💳 Metode Payment : {data['payment_method']}\n"
        f"🔢 Nomor Payment : `{data['payment_number']}`\n"
        f"📝 A/n : {data['owner_name']}\n"
        f"💰 Total Poin : {points}\n"
        f"🔗 Direferensi oleh : {referrer if referrer else 'Tidak ada'}"
    )
    await update.message.reply_text(summary, parse_mode="Markdown")

    date_joined = datetime.fromisoformat(data['created_at'])  

    # gunakan timezone-aware datetime
    now = datetime.now(timezone.utc)  

    if now - date_joined >= timedelta(days=180):
        if not has_badge(user_id, "💎 Veteran"):
            add_badge_to_user(user_id, "💎 Veteran")

async def myreferral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = get_user_by_id(user_id)
    if not data:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /register untuk daftar.")
        return

    username = data['username']
    points = data.get('points', 0)
    referrals = get_referrals_by_username(username)

    msg = (
        f"🔗 *Kode Referral Kamu*: `{username}`\n"
        f"💰 *Total Poin*: {points}\n"
        f"👥 *Member yang kamu undang*: {len(referrals)}"
    )

    if referrals:
        msg += "\n\n📋 *Daftar Referral:*\n"
        for i, ref in enumerate(referrals, 1):
            msg += f"{i}. {ref['username']}\n"
    else:
        msg += "\n\n📝 Belum ada yang menggunakan kode referral kamu."

    msg += (
        f"\n\n💡 *Tips:*\n"
        f"• Share kode referral `{username}` ke teman\n"
        f"• Setiap referral berhasil = +25 poin\n"
        f"• Gunakan /points untuk info lebih lanjut"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")

async def apply_job_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user_by_id(user_id)

    if not user_data:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /register untuk mendaftar.")
        return

    add_points_to_user(user_id, 2)
    user_data = get_user_by_id(user_id) # Ambil data terbaru setelah penambahan poin
    await update.message.reply_text(
        f"✅ Kamu mendapatkan +2 poin karena apply job!\n"
        f"Total poin kamu sekarang: {user_data['points']}"
    )

async def group_activity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user_by_id(user_id)

    if not user_data:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /register untuk mendaftar.")
        return
    
    add_points_to_user(user_id, 1)
    user_data = get_user_by_id(user_id) # Ambil data terbaru setelah penambahan poin
    await update.message.reply_text(
        f"✅ Kamu mendapatkan +1 poin karena aktif di grup!\n"
        f"Total poin kamu sekarang: {user_data['points']}"
    )

async def reset_point_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hanya admin yang bisa menggunakan command ini
    # Asumsikan admin_user_id adalah ID admin yang ditentukan di file konfigurasi atau hardcoded
    # Contoh: admin_user_id = "123456789"
    # Perlu penyesuaian jika ID admin tidak diketahui
    admin_user_id = "YOUR_ADMIN_USER_ID" # Ganti dengan ID admin yang sebenarnya

    if str(update.effective_user.id) != admin_user_id:
        await update.message.reply_text("❌ Kamu tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args:
        await update.message.reply_text("❌ Format salah. Gunakan: /resetpoint @username1 @username2 ...")
        return

    usernames_to_reset = context.args
    reset_count = 0
    
    for username in usernames_to_reset:
        # Hapus '@' jika ada di username
        username = username.lstrip('@')
        user_data = get_user_by_username(username)

        if user_data:
            user_id = user_data['user_id']
            # Reset poin menjadi 0
            add_user(user_id, {**user_data, 'points': 0}) # Menggunakan add_user untuk memperbarui data
            
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="✅ Poin kamu telah direset menjadi 0 oleh Admin."
                )
            except Exception:
                pass # Abaikan jika pesan tidak terkirim

            reset_count += 1
        else:
            await update.message.reply_text(f"❌ User dengan username '{username}' tidak ditemukan.")

    await update.message.reply_text(f"✅ Berhasil mereset poin untuk {reset_count} user.")


async def points_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user_by_id(user_id)

    if not user_data:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /register untuk mendaftar.")
        return

    points = user_data.get('points', 0)
    rupiah_equivalent = points * 10

    await update.message.reply_text(
        f"💰 *Informasi Poin Kamu*\n\n"
        f"🌟 Total Poin : {points}\n"
        f"💵 Nilai Rupiah : Rp {rupiah_equivalent}"
    )