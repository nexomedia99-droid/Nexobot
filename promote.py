from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import uuid
from datetime import datetime
import html


from db import (
    get_user_by_id, add_points_to_user,
    deduct_points, save_promotion, add_follower, get_promotion
)
from utils import GROUP_ID, PROMOTE_TOPIC_ID

# =======================================================================
# FUNGSI UNTUK PROMOSI STANDAR (/promote)
# =======================================================================
async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /promote command."""
    if update.message.chat.type != "private":
        await update.message.reply_text("❌ Perintah ini hanya bisa digunakan via DM dengan bot.")
        return
        
    user_id = str(update.effective_user.id)

    # 1. Pastikan pengguna sudah terdaftar dan memiliki poin yang cukup
    user_data = get_user_by_id(user_id)
    if not user_data:
        await update.message.reply_text("❌ Kamu harus terdaftar sebagai member untuk menggunakan fitur ini.")
        return

    if user_data['points'] < 10:
        await update.message.reply_text(f"❌ Poin kamu ({user_data['points']}) tidak cukup. Butuh minimal 10 poin.")
        return

    # 2. Ambil link dari input pengguna
    try:
        link = context.args[0]
        if not link.startswith(('http://', 'https://')):
            link = f"https://{link}"
    except IndexError:
        await update.message.reply_text("Silakan sertakan link. Contoh: /promote https://instagram.com/namakamu")
        return

    # 3. Kurangi poin dan simpan promosi ke database
    deduct_points(user_id, 10)
    promotion_id = str(uuid.uuid4())[:8]

    promotion_data = {
        'promo_id': promotion_id,
        'user_id': user_id,
        'link': link,
        'type': 'standar',
        'followers': []
    }
    save_promotion(promotion_data)

    # Notifikasi ke user
    await update.message.reply_text(
        f"✅ Promosi Anda telah dikonfirmasi. Saldo poin Anda dikurangi <b>10 poin</b>.",
        parse_mode="HTML"
    )
    await update.message.reply_text(
        f"🎉 Selamat !!\n"
        f"Promosi Anda berhasil diposting!\n"
        f"ID Promosi Anda: <code>{promotion_id}</code>\n"
        f"Gunakan ID ini untuk memeriksa pengklik dengan perintah:\n"
        f"<code>/cek_followers {promotion_id}</code>\n"
        f"⚠️ Jika terdapat kecurangan, segera laporkan ke admin.",
        parse_mode="HTML"
    )

    # 4. Buat tombol dan pesan promosi
    callback_data = f"promote:{promotion_id}"
    keyboard = [[InlineKeyboardButton("Follow & Get 1 Point", callback_data=callback_data)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    safe_username = html.escape(user_data['username'])
    safe_link = html.escape(link)

    message_text = (
        f"🎉 <b>TIME TO SUPPORT!</b> 🎉\n\n"
        f"✨ @{safe_username} lagi ngejar followers nih 🚴💨\n"
        f"Gas bantuin sekarang, jangan jadi penonton aja 🤡\n\n"
        f"👇 Klik tombol, dapet poin, dapet pahala sosial ✨"
    )


    # 5. Kirim pesan ke grup
    sent_message = await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=PROMOTE_TOPIC_ID,
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    # 6. Jadwalkan auto-delete setelah 24 jam (jika JobQueue tersedia)
    try:
        if context.job_queue:
            context.job_queue.run_once(
                delete_promotion_message,
                when=24*60*60,  # 24 jam dalam detik
                data={"chat_id": GROUP_ID, "message_id": sent_message.message_id}
            )
    except Exception as e:
        print(f"Warning: Auto-delete scheduling failed: {e}")


# =======================================================================
# FUNGSI UNTUK PROMOSI SPESIAL (/promote_special)
# =======================================================================
async def promote_special_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /promote_special command."""
    if update.message.chat.type != "private":
        await update.message.reply_text("❌ Perintah ini hanya bisa digunakan via DM dengan bot.")
        return
    
    user_id = str(update.effective_user.id)

    # Pastikan pengguna terdaftar dan punya poin yang cukup (15 poin)
    user_data = get_user_by_id(user_id)
    if not user_data:
        await update.message.reply_text("❌ Kamu harus terdaftar sebagai member untuk menggunakan fitur ini.")
        return

    if user_data['points'] < 15:
        await update.message.reply_text(f"❌ Poin kamu ({user_data['points']}) tidak cukup. Butuh minimal 15 poin.")
        return

    # Ambil link dari input pengguna
    try:
        link = context.args[0]
        if not link.startswith(('http://', 'https://')):
            link = f"https://{link}"
    except IndexError:
        await update.message.reply_text(
            "Silakan sertakan link. Contoh: /promote_special https://instagram.com/namakamu"
        )
        return

    # Kurangi poin dan simpan promosi ke database
    deduct_points(user_id, 15)
    promotion_id = str(uuid.uuid4())[:8]

    promotion_data = {
        'promo_id': promotion_id,
        'user_id': user_id,
        'link': link,
        'type': 'spesial',
        'followers': [],
        'timestamp': datetime.now()
    }
    save_promotion(promotion_data)

    # ✅ Notifikasi ke user (konfirmasi & ID promosi)
    await update.message.reply_text(
        f"✅ Promosi Spesial Anda telah dikonfirmasi. Saldo poin Anda dikurangi <b>15 poin</b>.",
        parse_mode="HTML"
    )
    await update.message.reply_text(
        f"Promosi Spesial berhasil diposting!\n"
        f"ID Promosi Anda: <code>{promotion_id}</code>\n"
        f"Gunakan ID ini untuk memeriksa pengklik dengan perintah:\n"
        f"<code>/cek_followers {promotion_id}</code>",
        parse_mode="HTML"
    )

    # Buat tombol dan pesan promosi
    callback_data = f"promote:{promotion_id}"
    keyboard = [[InlineKeyboardButton("Follow & Get 1 Point", callback_data=callback_data)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    safe_username = html.escape(user_data['username'])
    safe_link = html.escape(link)

    message_text = (
        "👑 <b>SPESIAL PROMOTE ALERT!</b> 👑\n\n"
        f"Hari ini giliran <b>@{safe_username}</b> naik ke spotlight ✨\n"
        "🚀 Bantu dia makin grow & dapetin vibes komunitas!\n\n"
        "🎁 Bonus: +1 poin buat kamu yang support lewat tombol di bawah!"
    )

    # Kirim pesan ke grup
    sent_message = await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=PROMOTE_TOPIC_ID,
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    # Pin pesan di grup
    await context.bot.pin_chat_message(
        chat_id=GROUP_ID,
        message_id=sent_message.message_id
    )

    # Jadwalkan auto-unpin 2 hari (jika JobQueue tersedia)
    try:
        if context.job_queue:
            context.job_queue.run_once(
                unpin_message,
                when=2*24*60*60,  # 2 hari dalam detik
                data={"chat_id": GROUP_ID, "message_id": sent_message.message_id}
            )
    except Exception as e:
        print(f"Warning: Auto-unpin scheduling failed: {e}")
    # Info terakhir ke user
    await update.message.reply_text(
        "✅ Promosi Spesial Anda telah berhasil diposting dan disematkan di grup."
    )


# =======================================================================
# BUTTON HANDLER
# =======================================================================
async def promote_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all inline button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith('promote:'):
        promo_id = query.data.split(':')[1]
        user_id = str(query.from_user.id)

        # 1. Ambil data promosi dari database
        promotion_data = get_promotion(promo_id)
        if not promotion_data:
            await query.answer("❌ Promosi ini tidak ditemukan.")
            return

        # 2. Periksa apakah pengguna sudah pernah mengklik
        if user_id in promotion_data['followers']:
            # Kirim DM peringatan kalau sudah pernah klik
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⚠️ Anda sudah pernah mendapatkan poin dari promosi ini. Klik Anda tidak dihitung lagi."
                )
            except Exception as e:
                print(f"Gagal mengirim DM ke pengguna {user_id}: {e}")
            await query.answer("Anda sudah pernah mendapatkan poin dari promosi ini.")
            return

        # 3. Tambah poin dan catat interaksi
        add_points_to_user(user_id, 1)  # Reward: 1 poin per click
        add_follower(promo_id, user_id)

        # 4. Kirim notifikasi DM
        try:
            link = promotion_data['link']
            # Pastikan link punya prefix
            if not link.startswith(("http://", "https://")):
                link = "https://" + link

            # Ambil data pemilik promosi untuk ditampilkan
            promo_owner = get_user_by_id(promotion_data['user_id'])
            owner_username = promo_owner['username'] if promo_owner else "Unknown"

            # Kirim pesan dengan link dan info poin
            dm_message = await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"🎉 <b>Terima kasih sudah support @{owner_username}!</b>\n\n"
                    f"🔗 <b>Link akun yang harus di-follow:</b>\n"
                    f"{link}\n\n"
                    f"🪙 <b>+1 poin</b> telah ditambahkan ke akun Anda!\n"
                    f"💰 Cek saldo poin dengan <code>/points</code>\n\n"
                    f"💡 <b>Tips:</b> Pastikan follow akun tersebut untuk mendukung member komunitas!\n"
                    f"⚠️ <b>Peringatan:</b> Jika ditemukan kecurangan, poin akan direset."
                ),
                parse_mode="HTML"
            )
            print(f"✅ DM berhasil dikirim ke user {user_id}, message_id: {dm_message.message_id}")
            
        except Exception as e:
            print(f"❌ Gagal mengirim DM ke pengguna {user_id}: {e}")
            # Tetap berikan feedback meski DM gagal
            await query.answer("⚠️ Poin ditambahkan, tapi DM gagal terkirim. Silakan hubungi admin untuk link.", show_alert=True)

        # 5. Kirim pop-up konfirmasi (bukan edit tombol)
        await query.answer("✅ Poin berhasil ditambahkan. Silakan cek DM dari saya untuk tautannya!")

# =======================================================================
# UTILITY FUNCTIONS
# =======================================================================
async def delete_promotion_message(context: ContextTypes.DEFAULT_TYPE):
    """Delete promotion message after 24 hours"""
    job = context.job
    try:
        await context.bot.delete_message(
            chat_id=job.data["chat_id"],
            message_id=job.data["message_id"]
        )
    except Exception as e:
        print(f"Failed to delete promotion message: {e}")

async def unpin_message(context: ContextTypes.DEFAULT_TYPE):
    """Unpin special promotion message after specified time"""
    job = context.job
    try:
        await context.bot.unpin_chat_message(
            chat_id=job.data["chat_id"],
            message_id=job.data["message_id"]
        )
    except Exception as e:
        print(f"Failed to unpin message: {e}")

# =======================================================================
# CEK FOLLOWERS
# =======================================================================
async def cek_followers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /cek_followers command."""
    user_id = str(update.effective_user.id)

    # 1. Pastikan pengguna memberikan ID promosi
    try:
        promo_id = context.args[0]
    except IndexError:
        await update.message.reply_text("Silakan sertakan ID promosi. Contoh: /cek_followers PROMO1234")
        return

    # 2. Ambil data promosi dari database
    promotion_data = get_promotion(promo_id)

    if not promotion_data:
        await update.message.reply_text("❌ Promosi dengan ID tersebut tidak ditemukan.")
        return

    # 3. Pastikan pengguna yang meminta adalah pemilik promosi
    if str(promotion_data['user_id']) != user_id:
        await update.message.reply_text("❌ Anda tidak memiliki izin untuk melihat data promosi ini.")
        return

    # 4. Ambil daftar follower dan username mereka
    follower_ids = promotion_data['followers']
    follower_usernames = []

    for follower_id in follower_ids:
        follower_user_data = get_user_by_id(follower_id)
        if follower_user_data:
            follower_usernames.append(f"• @{follower_user_data['username']}")
        else:
            follower_usernames.append("• Pengguna tidak ditemukan")

    usernames_list = "\n".join(follower_usernames)

    # 5. Kirim laporan
    report_text = (
        f"📋 <b>Laporan Pengklik Promosi {promo_id}</b>\n\n"
        f"<b>Total klik:</b> {len(follower_ids)}\n\n"
        f"<b>Daftar username:</b>\n"
        f"{usernames_list}\n"
        f"silahkan di cek kembali, laporkan ke admin jika tidak sesuai."
    )

    await update.message.reply_text(
        report_text,
        parse_mode="HTML"
    )
