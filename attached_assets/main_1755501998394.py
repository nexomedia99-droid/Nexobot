from db import init_db
from keep_alive import keep_alive
from dashboard import start_dashboard, log_activity
import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ConversationHandler, ContextTypes
)
from utils import ensure_env, BOT_TOKEN
from start import start, menu_command, button_handler, new_member_handler, hidden_tag_handler
from register import (
    register_command, username_step, referral_step, whatsapp_step, telegram_step,
    payment_method_step, payment_number_step, owner_name_step,
    editinfo_command, choose_field_step, edit_username_step, edit_whatsapp_step, edit_telegram_step,
    edit_payment_method_step, edit_payment_number_step, edit_owner_name_step,
    myinfo_command, myreferral_command,
    USERNAME, REFERRAL, WHATSAPP, TELEGRAM, PAYMENT_METHOD, PAYMENT_NUMBER, OWNER_NAME,
    CHOOSE_FIELD, EDIT_USERNAME, EDIT_WHATSAPP, EDIT_TELEGRAM, EDIT_PAYMENT_METHOD, EDIT_PAYMENT_NUMBER, EDIT_OWNER_NAME
)
from ai import chat_with_ai, stop_ai_chat, start_ai_chat, save_group_messages, summary_command, group_activity_points
from admin import listmember_command, paymentinfo_command, memberinfo_command, delete_member_command, resetpoint_command, addbadge_command, resetapply_command, resetbadge_command
from jobs import postjob_conv, postjob_command, updatejob_command, resetjob_command, pelamarjob_command, listjob_command, infojob_command, apply_button
from help import help_command
from leaderboard import leaderboard_command, points_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    init_db()
    ensure_env()

    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler untuk register
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register_command, filters=filters.ChatType.PRIVATE)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username_step)],
            REFERRAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, referral_step)],
            WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, whatsapp_step)],
            TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_step)],
            PAYMENT_METHOD: [CallbackQueryHandler(payment_method_step)],
            PAYMENT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_number_step)],
            OWNER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, owner_name_step)],
        },
        fallbacks=[],
    )

    # Conversation handler untuk editinfo
    editinfo_conv = ConversationHandler(
        entry_points=[CommandHandler("editinfo", editinfo_command)],
        states={
            CHOOSE_FIELD: [CallbackQueryHandler(choose_field_step)],
            EDIT_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_username_step)],
            EDIT_WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_whatsapp_step)],
            EDIT_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_telegram_step)],
            EDIT_PAYMENT_METHOD: [CallbackQueryHandler(edit_payment_method_step)],
            EDIT_PAYMENT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_payment_number_step)],
            EDIT_OWNER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_owner_name_step)],
        },
        fallbacks=[],
    )
    application.add_handler(editinfo_conv)

    # === Conversation Register ===
    application.add_handler(conv_handler)
    application.add_handler(
        CommandHandler("register",
            lambda u, c: u.message.reply_text("❌ Pendaftaran hanya via private chat. DM bot ya!"),
            filters=filters.ChatType.GROUPS
        )
    )

    application.add_handler(CommandHandler("myinfo", myinfo_command))
    application.add_handler(CommandHandler("editinfo", editinfo_command))
    application.add_handler(CommandHandler("myreferral", myreferral_command))

    # Jobs Feature
    application.add_handler(postjob_conv)
    # Admin
    application.add_handler(CommandHandler("postjob", postjob_command))
    application.add_handler(CommandHandler("updatejob", updatejob_command))
    application.add_handler(CommandHandler("resetjob", resetjob_command))
    application.add_handler(CommandHandler("pelamarjob", pelamarjob_command))

    # Member
    application.add_handler(CommandHandler("listjob", listjob_command))
    application.add_handler(CommandHandler("infojob", infojob_command))

    # Apply button
    application.add_handler(CallbackQueryHandler(apply_button, pattern=r"^apply_\d+$"))
    
    
    # === Menu & Start ===
    application.add_handler(
        CommandHandler("start", start, filters=filters.ChatType.PRIVATE)
    )
    application.add_handler(
        CommandHandler("start", lambda u, c: u.message.reply_text("❌ Command /start hanya bisa digunakan di private chat (DM bot)."), filters=filters.ChatType.GROUPS)
    )
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    # === Special Messages ===
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\..+'), hidden_tag_handler))

    # === AI Features ===
    # 1. start/stop interactive mode
    application.add_handler(CommandHandler("startai", start_ai_chat))
    application.add_handler(CommandHandler("stopai", stop_ai_chat))

    # 2. AI di grup: /ai <text>
    application.add_handler(CommandHandler("ai", chat_with_ai))

    # 3. AI di private chat: interaktif TANPA /ai
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, chat_with_ai)
    )
    # 4. summary fitur
    application.add_handler(CommandHandler("summary", summary_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_group_messages))
    
    # 5. Group activity points (2 points for active participation)
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, group_activity_points))

    # === Admin Features ===
    application.add_handler(CommandHandler("listmember", listmember_command))
    application.add_handler(CommandHandler("paymentinfo", paymentinfo_command))
    application.add_handler(CommandHandler("memberinfo", memberinfo_command))
    application.add_handler(CommandHandler("delete", delete_member_command))
    application.add_handler(CommandHandler("resetpoint", resetpoint_command))

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("points", points_command))
    application.add_handler(CommandHandler("addbadge", addbadge_command))

    application.add_handler(CommandHandler("resetapply", resetapply_command))
    application.add_handler(CommandHandler("resetbadge", resetbadge_command))


    keep_alive()
    print("🌐 Keep-alive server started on port 8080")
    
    start_dashboard()
    print("📊 Dashboard server started on port 5000")

    print("🤖 Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()