from telegram import Update
from telegram.ext import ContextTypes
from decorators import admin_only
from db import get_all_users, get_user_by_username, delete_user_by_id, add_badge_to_user, has_badge, get_conn


# ======================
# ADMIN COMMANDS
# ======================

# /listmember
@admin_only
async def listmember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = [data["username"] for data in get_all_users()]
    total = len(members)

    if not members:
        await update.message.reply_text("📂 Belum ada member yang terdaftar.")
        return

    text = "📋 *Daftar Member Terdaftar*\n\n"
    text += "\n".join([f"{i+1}. {username}" for i, username in enumerate(members)])
    text += f"\n\n👥 Total: {total} member"

    await update.message.reply_text(text, parse_mode="Markdown")


# /paymentinfo username1 username2 ...
@admin_only
async def paymentinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Gunakan format: /paymentinfo username1 username2 ..."
        )
        return

    usernames = [arg.strip() for arg in context.args]
    results = []

    for i, uname in enumerate(usernames, start=1):
        user_data = get_user_by_username(uname)
        if not user_data:
            results.append(f"{i}. {uname}\n❌ Tidak ditemukan.")
        else:
            results.append(
                f"{i}. {user_data['username']}\n"
                f"💳 Metode Payment : {user_data['payment_method']}\n"
                f"🔢 Nomor : `{user_data['payment_number']}`\n"
                f"📝 A/n : {user_data['owner_name']}"
            )

    reply_text = "📂 *Informasi Payment*\n\n" + "\n\n".join(results)
    await update.message.reply_text(reply_text, parse_mode="Markdown")


# /memberinfo username1 username2 ... | /memberinfo all
@admin_only
async def memberinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Gunakan format: /memberinfo username1 username2 ... atau /memberinfo all"
        )
        return

    if len(context.args) == 1 and context.args[0].lower() == "all":
        # tampilkan semua member
        all_users = get_all_users()
        if not all_users:
            await update.message.reply_text("❌ Belum ada member yang terdaftar.")
            return
        results = []
        for i, data in enumerate(all_users, start=1):
            results.append(
                f"{i}. 👤 {data['username']}\n"
                f"☎️ WhatsApp : `{data['whatsapp']}`\n"
                f"📱 Telegram : `{data['telegram']}`\n"
                f"💳 Metode Payment : {data['payment_method']}\n"
                f"🔢 Nomor Payment : `{data['payment_number']}`\n"
                f"📝 A/n : {data['owner_name']}"
            )
        reply_text = "📂 *Informasi Semua Member*\n\n" + "\n\n".join(results)
        await update.message.reply_text(reply_text, parse_mode="Markdown")
        return

    # kalau bukan all → cek satu/satu
    usernames = [arg.strip() for arg in context.args]
    results = []

    for i, uname in enumerate(usernames, start=1):
        user_data = get_user_by_username(uname)
        if not user_data:
            results.append(f"{i}. {uname}\n❌ Tidak ditemukan.")
        else:
            results.append(
                f"{i}. 👤 {user_data['username']}\n"
                f"☎️ WhatsApp : `{user_data['whatsapp']}`\n"
                f"📱 Telegram : `{user_data['telegram']}`\n"
                f"💳 Metode Payment : {user_data['payment_method']}\n"
                f"🔢 Nomor Payment : `{user_data['payment_number']}`\n"
                f"📝 A/n : {user_data['owner_name']}"
            )

    reply_text = "📂 *Informasi Member*\n\n" + "\n\n".join(results)
    await update.message.reply_text(reply_text, parse_mode="Markdown")

#========ADD BADGE===========
@admin_only
async def addbadge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Gunakan: /addbadge <username> <badge>")
        return

    username, badge_name = context.args[0], " ".join(context.args[1:])
    user = get_user_by_username(username)
    if not user:
        await update.message.reply_text("❌ User tidak ditemukan.")
        return

    if has_badge(user['user_id'], badge_name):
        await update.message.reply_text(f"⚠️ {username} sudah punya badge '{badge_name}'")
        return

    add_badge_to_user(user['user_id'], badge_name)
    await update.message.reply_text(f"✅ Badge '{badge_name}' ditambahkan ke {username}")
# /delete username1 username2 ...
@admin_only
async def delete_member_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Gunakan format: /delete username1 username2 ...\n"
            "Contoh: /delete user123 user456"
        )
        return

    usernames = [arg.strip() for arg in context.args]
    results = []
    deleted_count = 0

    for i, username in enumerate(usernames, start=1):
        user_data = get_user_by_username(username)
        if not user_data:
            results.append(f"{i}. ❌ {username} - Tidak ditemukan")
        else:
            try:
                # Delete user from database
                delete_user_by_id(user_data['user_id'])
                results.append(f"{i}. ✅ {username} - Berhasil dihapus")
                deleted_count += 1

                # Send notification to deleted user (optional)
                try:
                    await context.bot.send_message(
                        chat_id=user_data['user_id'],
                        text=(
                            "⚠️ *Akun kamu telah dihapus oleh admin*\n\n"
                            "Kamu bisa mendaftar ulang kapan saja dengan /register"
                        ),
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass  # User might have blocked the bot

            except Exception as e:
                results.append(f"{i}. ❌ {username} - Gagal dihapus: {str(e)}")

    reply_text = (
        f"🗑️ *Hasil Penghapusan Member*\n\n"
        + "\n".join(results) +
        f"\n\n📊 *Summary:* {deleted_count}/{len(usernames)} member berhasil dihapus"
    )

    await update.message.reply_text(reply_text, parse_mode="Markdown")


# /resetpoint username1 username2 ...
@admin_only
async def resetpoint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Gunakan format: /resetpoint username1 username2 ... atau /resetpoint all\n"
            "Contoh: /resetpoint user123 user456\n"
            "Contoh: /resetpoint all"
        )
        return

    # ==== Tambahan: reset semua ====
    if len(context.args) == 1 and context.args[0].lower() == "all":
        try:
            from db import get_conn
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE users SET points = 0")
                conn.commit()

            await update.message.reply_text("✅ Semua poin member berhasil direset ke 0")
            return
        except Exception as e:
            await update.message.reply_text(f"❌ Gagal reset semua poin: {str(e)}")
            return

    # ==== Reset by username (kode lama) ====
    usernames = [arg.strip() for arg in context.args]
    results = []
    reset_count = 0

    for i, username in enumerate(usernames, start=1):
        user_data = get_user_by_username(username)
        if not user_data:
            results.append(f"{i}. ❌ {username} - Tidak ditemukan")
        else:
            try:
                from db import get_conn
                with get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET points = 0 WHERE user_id = ?", (user_data['user_id'],))
                    conn.commit()

                results.append(f"{i}. ✅ {username} - Poin berhasil direset")
                reset_count += 1
            except Exception as e:
                results.append(f"{i}. ❌ {username} - Gagal reset: {str(e)}")

    reply_text = (
        f"🔄 *Hasil Reset Poin*\n\n"
        + "\n".join(results) +
        f"\n\n📊 *Summary:* {reset_count}/{len(usernames)} member berhasil direset"
    )
    await update.message.reply_text(reply_text, parse_mode="Markdown")

#========RESET APPLY===========
@admin_only
async def resetapply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Gunakan format: /resetapply <username>\n"
            "Contoh: /resetapply user123"
        )
        return

    username = context.args[0].strip()
    user_data = get_user_by_username(username)
    if not user_data:
        await update.message.reply_text(f"❌ Username '{username}' tidak ditemukan.")
        return

    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM applicants WHERE user_id = ?", (user_data['user_id'],))
            conn.commit()

        await update.message.reply_text(
            f"✅ Semua data apply untuk *{username}* berhasil dihapus.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal reset apply: {str(e)}")


#=========RESET BADGE===========
@admin_only
async def resetbadge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Gunakan format: /resetbadge <username>\n"
            "Contoh: /resetbadge user123"
        )
        return

    username = context.args[0].strip()
    user_data = get_user_by_username(username)
    if not user_data:
        await update.message.reply_text(f"❌ Username '{username}' tidak ditemukan.")
        return

    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM achievements WHERE user_id = ?", (user_data['user_id'],))
            conn.commit()

        await update.message.reply_text(
            f"✅ Semua badge untuk *{username}* berhasil dihapus.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal reset badge: {str(e)}")