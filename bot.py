from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID

from database import create_tables
from keyboards import (
    main_menu,
    admin_menu,
)

from handlers.main_menu import (
    show_main_menu,
    main_menu_handler,
)

# =====================================
# USER HANDLERS
# =====================================

from handlers.registration import registration_handler
from handlers.profile import profile_handler
from handlers.wallet import wallet
from handlers.wallet import wallet_handler
from handlers.fund_wallet import fund_wallet, fund_wallet_handler
from handlers.deposit import deposit_handler, select_btc, deposit_command
from handlers.submit_tx import submit_tx_handler
from handlers.history import history_handler
from handlers.history import withdrawal_history_handler
from handlers.referrals import referral_handler
from handlers.refund import refund_handler
from handlers.check_status import check_status_handler
from handlers.help import help_handler
from handlers.faq import faq_handler
from handlers.terms import terms_handler
from handlers.privacy import privacy_handler
from handlers.page_registry import register_page
from handlers.navigation import clear_navigation
from handlers.navigation import push_page
from handlers.navigation import back_handler
from handlers.admin_wallet import admin_wallet_handler
from handlers.withdraw import withdraw_handler
from handlers.change_withdrawal_address import (
    change_withdrawal_address_handler,
)

# =====================================
# CLOUD MINING
# =====================================

from handlers.mining import (
    mining_handler,
    buy_hashpower_handler,
    claim_rewards_handler,
    contracts_handler,
)

# =====================================
# SUPPORT
# =====================================

from handlers.vip_support import (
    vip_support_handler,
    vip_support_main_menu_handler,
)

from handlers.support_reply import (
    reply_handler,
)

# =====================================
# KYC
# =====================================

from handlers.kyc import (
    kyc_handler,
    kyc_status,
)

from handlers.kyc_admin import (
    approve_kyc_handler,
    reject_kyc_handler,
    kyc_callback_handler,
)

# =====================================
# ADMIN PANEL
# =====================================

from handlers.admin_panel import (
    admin_panel_handler,
    pending_kyc_handler,
    pending_deposits_handler,
    pending_withdrawals_handler,
    pending_refunds_handler,
    deposit_callback_handler,
    refund_callback_handler,
    withdrawal_handler,
)

# =====================================
# START
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.args:
        try:
            context.user_data["referrer_id"] = int(context.args[0])
        except ValueError:
            pass

    await show_main_menu(update, context)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)
    
# =====================================
# HELP COMMAND
# =====================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "ℹ️ Nebumine pro Bot\n\n"
        "Use the menu buttons to access the available features."
    )


# =====================================
# GLOBAL MENU BUTTONS
# =====================================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "🏠 Main Menu":

        await show_main_menu(update, context)
        return

    elif text == "🪪 KYC Status":

        await kyc_status(update, context)
        return

    elif text == "🛠 Admin Panel":

        if update.effective_user.id != ADMIN_ID:

            await update.message.reply_text(
                "❌ Access denied."
            )

        return

# =====================================
# MAIN
# =====================================

def main():

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    # =====================================
    # SLASH COMMANDS
    # =====================================

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(deposit_handler)
    
    # =====================================
    # UNIVERSAL BACK BUTTON
    # =====================================
    
    app.add_handler(back_handler)

    # =====================================
    # CONVERSATION HANDLERS FIRST
    # =====================================

    app.add_handler(registration_handler)
    app.add_handler(kyc_handler)
    app.add_handler(deposit_handler)
    app.add_handler(submit_tx_handler)
    app.add_handler(refund_handler)
    app.add_handler(vip_support_handler)
    app.add_handler(vip_support_main_menu_handler)
    app.add_handler(help_handler)
    app.add_handler(faq_handler)
    app.add_handler(terms_handler)
    app.add_handler(privacy_handler)
    app.add_handler(withdraw_handler)
    app.add_handler(change_withdrawal_address_handler)

    # =====================================
    # NORMAL USER HANDLERS
    # =====================================

    app.add_handler(profile_handler)
    app.add_handler(wallet_handler)
    app.add_handler(fund_wallet_handler)
    app.add_handler(history_handler)
    app.add_handler(withdrawal_history_handler)
    app.add_handler(referral_handler)
    app.add_handler(check_status_handler)

    # =====================================
    # CLOUD MINING
    # =====================================

    app.add_handler(mining_handler)
    app.add_handler(buy_hashpower_handler)
    app.add_handler(claim_rewards_handler)
    app.add_handler(contracts_handler)

    # =====================================
    # ADMIN PANEL
    # =====================================

    app.add_handler(admin_panel_handler)
    app.add_handler(pending_kyc_handler)
    app.add_handler(pending_deposits_handler)
    app.add_handler(pending_withdrawals_handler)
    app.add_handler(deposit_callback_handler)
    app.add_handler(withdrawal_handler)
    app.add_handler(pending_refunds_handler)
    app.add_handler(refund_callback_handler)
    
    # ===========================
    # ADMIN WALLET ADJUSTMENT
    # ===========================

    app.add_handler(admin_wallet_handler)

    # =====================================
    # KYC CALLBACKS
    # =====================================

    app.add_handler(approve_kyc_handler)
    app.add_handler(reject_kyc_handler)
    app.add_handler(kyc_callback_handler)

    # =====================================
    # SUPPORT REPLIES
    # =====================================
    
    app.add_handler(reply_handler)

    # =====================================
    # GLOBAL MENU BUTTONS
    # =====================================

    menu_filter = filters.Regex(
        r"^(🏠 Main Menu|🪪 KYC Status|🛠 Admin Panel)$"
    )

    app.add_handler(
        MessageHandler(
            menu_filter,
            buttons,
        )
    )
    
    # =====================================
    # PAGE REGISTRY
    # =====================================

    register_page(
        "main_menu",
        show_main_menu,
    )

    register_page(
        "wallet",
        wallet,
    )
    
    register_page(
    "fund_wallet",
    fund_wallet,
    )
    
    register_page(
    "deposit",
    select_btc,
    )
    
    print("✅ Nebumine pro Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
