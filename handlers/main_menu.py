from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from config import ADMIN_ID
from keyboards import main_menu, admin_menu

from handlers.navigation import (
    clear_navigation,
    push_page,
)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("========== MAIN MENU OPENED ==========")

    # Reset navigation
    clear_navigation(context)

    push_page(context, "main_menu")

    print("Navigation Stack:", context.user_data.get("navigation_stack"))
    print("======================================")

    await update.message.reply_text(
        "🏠 Main Menu",
        reply_markup=(
            admin_menu
            if update.effective_user.id == ADMIN_ID
            else main_menu
        ),
    )


main_menu_handler = MessageHandler(
    filters.Regex("^🏠 Main Menu$"),
    show_main_menu,
    )
