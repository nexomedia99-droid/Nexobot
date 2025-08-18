from telegram import Update
from telegram.ext import ContextTypes
from decorators import admin_only
from db import (
    get_all_users, get_user_by_username, delete_user_by_id, add_points_to_user,
    add_badge_to_user, get_badges, get_conn
)
from utils import sanitize_input, get_user_display_name
from dashboard import log_activity
import logging

logger = logging.getLogger(__name__)

@admin_only
async def listmember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all registered members"""
    try:
        users = get_all_users()
        
        if not users:
            await update.message.reply_text("📭 Belum ada member yang terdaftar.")
            return
        
        # Split into chunks of 20 for better readability
        chunk_size = 20
        total_chunks = (len(users) + chunk_size - 1) // chunk_size
        
        page = 1
        if context.args and context.args[0].isdigit():
            page = max(1, min(int(context.args[0]), total_chunks))
        
        start_idx = (page - 1) * chunk_size
        end_idx = min(start_idx + chunk_size, len(users))
        
        text = f"👥 *Daftar Member* (Page {page}/{total_chunks})\n"
        text += f"Total: {len(users)} member\n\n"
        
        for i, user in enumerate(users[start_idx:end_idx], start=start_idx + 1):
            points = user.get('points', 0)
            text += f"{i}. `{user['username']}` - {points} poin\n"
        
        if total_chunks > 1:
            text += f"\n📄 Gunakan `/listmember <page>` untuk halaman lain"
        
        await update.message.reply_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Failed to list members: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mengambil daftar member.")

@admin_only
async def memberinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get detailed member information"""
    if not context.args:
        await update.message.reply_text(
            "📋 *Penggunaan:*\n"
            "`/memberinfo <username1> <username2> ...`\n"
            "`/memberinfo all` - Info semua member",
            parse_mode="Markdown"
        )
        return
    
    try:
        if context.args[0].lower() == "all":
            users = get_all_users()
            if not users:
                await update.message.reply_text("📭 Belum ada member yang terdaftar.")
                return
            
            # Limit to first 10 for "all"
            users = users[:10]
            text = f"👥 *Info Semua Member* (10 pertama)\n\n"
        else:
            usernames = [sanitize_input(arg) for arg in context.args]
            users = []
            not_found = []
            
            for username in usernames:
                user = get_user_by_username(username)
                if user:
                    users.append(user)
                else:
                    not_found.append(username)
            
            if not_found:
                await update.message.reply_text(
                    f"❌ Username tidak ditemukan: {', '.join(not_found)}"
                )
                return
            
            text = f"👤 *Info Member*\n\n"
        
        for i, user in enumerate(users, 1):
            badges = get_badges(user['user_id'])
            badge_text = " | ".join(badges) if badges else "Belum ada"
            
            text += (
                f"**{i}. {user['username']}**\n"
                f"🆔 ID: `{user['user_id']}`\n"
                f"🏅 Badge: {badge_text}\n"
                f"💰 Points: {user.get('points', 0)}\n"
                f"☎️ WhatsApp: `{user['whatsapp']}`\n"
                f"📱 Telegram: `{user['telegram']}`\n"
                f"🔗 Referrer: {user.get('referrer', 'Tidak ada')}\n\n"
            )
        
        # Split message if too long
        if len(text) > 4000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Failed to get member info: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mengambil info member.")

@admin_only
async def paymentinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get payment information for members"""
    if not context.args:
        await update.message.reply_text(
            "💳 *Penggunaan:*\n"
            "`/paymentinfo <username1> <username2> ...`",
            parse_mode="Markdown"
        )
        return
    
    try:
        usernames = [sanitize_input(arg) for arg in context.args]
        users = []
        not_found = []
        
        for username in usernames:
            user = get_user_by_username(username)
            if user:
                users.append(user)
            else:
                not_found.append(username)
        
        if not_found:
            await update.message.reply_text(
                f"❌ Username tidak ditemukan: {', '.join(not_found)}"
            )
            return
        
        text = "💳 *Info Payment Member*\n\n"
        
        for i, user in enumerate(users, 1):
            text += (
                f"**{i}. {user['username']}**\n"
                f"💳 Metode: {user['payment_method']}\n"
                f"🔢 Nomor: `{user['payment_number']}`\n"
                f"📝 A/n: {user['owner_name']}\n"
                f"☎️ WhatsApp: `{user['whatsapp']}`\n\n"
            )
        
        await update.message.reply_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Failed to get payment info: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mengambil info payment.")

@admin_only
async def delete_member_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete members from database"""
    if not context.args:
        await update.message.reply_text(
            "🗑️ *Penggunaan:*\n"
            "`/delete <username1> <username2> ...`",
            parse_mode="Markdown"
        )
        return
    
    try:
        usernames = [sanitize_input(arg) for arg in context.args]
        deleted = []
        not_found = []
        
        for username in usernames:
            user = get_user_by_username(username)
            if user:
                delete_user_by_id(user['user_id'])
                deleted.append(username)
                log_activity("delete_member", user['user_id'], f"Member {username} deleted by admin")
            else:
                not_found.append(username)
        
        result_text = ""
        if deleted:
            result_text += f"✅ Berhasil menghapus: {', '.join(deleted)}\n"
        if not_found:
            result_text += f"❌ Tidak ditemukan: {', '.join(not_found)}"
        
        await update.message.reply_text(result_text)
        
    except Exception as e:
        logger.error(f"Failed to delete members: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat menghapus member.")

@admin_only
async def resetpoint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset member points to 0"""
    if not context.args:
        await update.message.reply_text(
            "🔄 *Penggunaan:*\n"
            "`/resetpoint <username1> <username2> ...`",
            parse_mode="Markdown"
        )
        return
    
    try:
        usernames = [sanitize_input(arg) for arg in context.args]
        reset = []
        not_found = []
        
        for username in usernames:
            user = get_user_by_username(username)
            if user:
                # Reset points by setting to 0
                with get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE users SET points = 0, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                        (user['user_id'],)
                    )
                    conn.commit()
                
                reset.append(username)
                log_activity("reset_points", user['user_id'], f"Points reset for {username}")
            else:
                not_found.append(username)
        
        result_text = ""
        if reset:
            result_text += f"✅ Points direset untuk: {', '.join(reset)}\n"
        if not_found:
            result_text += f"❌ Tidak ditemukan: {', '.join(not_found)}"
        
        await update.message.reply_text(result_text)
        
    except Exception as e:
        logger.error(f"Failed to reset points: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mereset points.")

@admin_only
async def addbadge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add badge to member"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "🏅 *Penggunaan:*\n"
            "`/addbadge <username> <badge_name>`\n\n"
            "*Contoh Badge:*\n"
            "🌟 New Member\n"
            "🎯 Member Aktif\n"
            "💼 Worker Pro\n"
            "🏆 Top Contributor\n"
            "🚀 Rising Star\n"
            "🔥 Fast Responder",
            parse_mode="Markdown"
        )
        return
    
    try:
        username = sanitize_input(context.args[0])
        badge_name = sanitize_input(" ".join(context.args[1:]))
        
        user = get_user_by_username(username)
        if not user:
            await update.message.reply_text(f"❌ Username `{username}` tidak ditemukan.", parse_mode="Markdown")
            return
        
        # Check if user already has the badge
        existing_badges = get_badges(user['user_id'])
        if badge_name in existing_badges:
            await update.message.reply_text(f"⚠️ `{username}` sudah memiliki badge `{badge_name}`", parse_mode="Markdown")
            return
        
        add_badge_to_user(user['user_id'], badge_name)
        
        await update.message.reply_text(
            f"✅ Badge `{badge_name}` berhasil ditambahkan ke `{username}`",
            parse_mode="Markdown"
        )
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=user['user_id'],
                text=f"🎉 Selamat! Kamu mendapat badge baru: *{badge_name}*",
                parse_mode="Markdown"
            )
        except:
            pass  # User might have blocked bot
        
        log_activity("add_badge", user['user_id'], f"Badge '{badge_name}' added by admin")
        
    except Exception as e:
        logger.error(f"Failed to add badge: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat menambahkan badge.")

@admin_only
async def resetapply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset job applications for specific user or all"""
    if not context.args:
        await update.message.reply_text(
            "🔄 *Penggunaan:*\n"
            "`/resetapply <username>` - Reset apply user tertentu\n"
            "`/resetapply all` - Reset semua apply",
            parse_mode="Markdown"
        )
        return
    
    try:
        if context.args[0].lower() == "all":
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM applicants")
                conn.commit()
            
            await update.message.reply_text("✅ Semua aplikasi job telah direset.")
            log_activity("reset_apply", None, "All job applications reset by admin")
            
        else:
            username = sanitize_input(context.args[0])
            user = get_user_by_username(username)
            
            if not user:
                await update.message.reply_text(f"❌ Username `{username}` tidak ditemukan.", parse_mode="Markdown")
                return
            
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM applicants WHERE user_id = ?", (user['user_id'],))
                conn.commit()
            
            await update.message.reply_text(f"✅ Aplikasi job untuk `{username}` telah direset.", parse_mode="Markdown")
            log_activity("reset_apply", user['user_id'], f"Job applications reset for {username}")
        
    except Exception as e:
        logger.error(f"Failed to reset applications: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mereset aplikasi.")

@admin_only
async def resetbadge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset badges for specific user or all"""
    if not context.args:
        await update.message.reply_text(
            "🔄 *Penggunaan:*\n"
            "`/resetbadge <username>` - Reset badge user tertentu\n"
            "`/resetbadge all` - Reset semua badge",
            parse_mode="Markdown"
        )
        return
    
    try:
        if context.args[0].lower() == "all":
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM achievements")
                conn.commit()
            
            await update.message.reply_text("✅ Semua badge telah direset.")
            log_activity("reset_badges", None, "All badges reset by admin")
            
        else:
            username = sanitize_input(context.args[0])
            user = get_user_by_username(username)
            
            if not user:
                await update.message.reply_text(f"❌ Username `{username}` tidak ditemukan.", parse_mode="Markdown")
                return
            
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM achievements WHERE user_id = ?", (user['user_id'],))
                conn.commit()
            
            await update.message.reply_text(f"✅ Badge untuk `{username}` telah direset.", parse_mode="Markdown")
            log_activity("reset_badges", user['user_id'], f"Badges reset for {username}")
        
    except Exception as e:
        logger.error(f"Failed to reset badges: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mereset badge.")
