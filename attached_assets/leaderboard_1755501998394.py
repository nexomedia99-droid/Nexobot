
from telegram import Update
from telegram.ext import ContextTypes
from db import get_all_users

#======LEADERBOARD======
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from db import get_all_users, add_badge, has_badge  # import fungsi badge
    users = get_all_users()

    # === Hitung leaderboard ===
    # Top by points
    top_points = sorted(users, key=lambda x: x.get('points', 0), reverse=True)[:10]

    # Top by referrals
    top_referrals = sorted(users, key=lambda x: x.get('referrals', 0), reverse=True)[:10]

    # === Tambah badge otomatis ke user dengan poin tertinggi ===
    if top_points:  # pastikan ada user
        top_user = top_points[0]  # user dengan poin tertinggi (rank 1)
        if not has_badge(top_user['user_id'], "🏆 Top Contributor"):
            # kasih badge kalau belum punya
            add_badge(top_user['user_id'], "🏆 Top Contributor")
            try:
                await context.bot.send_message(
                    chat_id=top_user['user_id'],
                    text="🏆 Selamat! Kamu jadi *Top Contributor* bulan ini!",
                    parse_mode="Markdown"
                )
            except:
                pass  # biar gak error kalau user belum bisa di-DM

    # === Tampilkan leaderboard ke chat ===
    text = "🏆 *LEADERBOARD*\n\n"
    text += "💰 *Top Points:*\n"
    for i, user in enumerate(top_points, start=1):
        text += f"{i}. {user['username']} - {user.get('points',0)} poin\n"

    text += "\n👥 *Top Referrers:*\n"
    for i, user in enumerate(top_referrals, start=1):
        text += f"{i}. {user['username']} - {user.get('referrals',0)} referral\n"

    await update.message.reply_text(text, parse_mode="Markdown")

#======POINTS======
async def points_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's current points"""
    user_id = str(update.effective_user.id)
    from db import get_user_by_id
    
    data = get_user_by_id(user_id)
    if not data:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /register untuk daftar.")
        return
    
    points = data.get('points', 0)
    msg = f"💰 *Poin Kamu: {points}*\n\n"
    msg += "📈 *Cara Mendapat Poin:*\n"
    msg += "• Apply job: +2 poin\n"
    msg += "• Aktif di grup: +1 poin/hari\n"
    msg += "• 1 referral berhasil: +25 poin\n\n"
    msg += "💰 *Nilai Tukar: 1 poin = Rp 10*\n\n"
    msg += "💡 Gunakan /myreferral untuk cek referral kamu!"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
