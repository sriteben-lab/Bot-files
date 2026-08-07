from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from keyboards import (
    wallet_menu,
    cancel_menu,
)

from config import ADMIN_ID

from database import (
    get_kyc_status,
    get_wallet_balance,
    has_active_contract,
    create_withdrawal,
    admin_wallet_adjustment,
    record_wallet_transaction,
)

CRYPTO, AMOUNT, ADDRESS = range(3)

withdraw_crypto_keyboard = ReplyKeyboardMarkup(
    [
        ["₿ Withdraw BTC", "♦ Withdraw ETH"],
        ["💲 Withdraw USDT (TRC20)"],
        ["💲 Withdraw USDT (ERC20)"],
        ["💲 Withdraw USDC (ERC20)"],
        ["❌ Cancel"],
    ],
    resize_keyboard=True,
)


# ==========================================
# START WITHDRAWAL
# ==========================================

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    status = get_kyc_status(update.effective_user.id)

    if status != "Approved":

        await update.message.reply_text(
            "❌ Withdrawal Unavailable\n\n"
            "Your KYC verification has not been approved.\n\n"
            "You must complete KYC before requesting a withdrawal.",
            reply_markup=wallet_menu,
        )

        return ConversationHandler.END

    await update.message.reply_text(
        "💸 Withdrawal Request\n\n"
        "Select the cryptocurrency you want to withdraw.",
        reply_markup=withdraw_crypto_keyboard,
    )

    return CRYPTO

# ==========================================
# RECEIVE CRYPTO
# ==========================================

async def receive_crypto(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message.text == "❌ Cancel":
        return await cancel(update, context)

    crypto_map = {
        "₿ Withdraw BTC": "BTC",
        "♦ Withdraw ETH": "ETH",
        "💲 Withdraw USDT (TRC20)": "USDT TRC20",
        "💲 Withdraw USDT (ERC20)": "USDT ERC20",
        "💲 Withdraw USDC (ERC20)": "USDC ERC20",
    }

    if update.message.text not in crypto_map:

        await update.message.reply_text(
            "❌ Please select a cryptocurrency using the buttons."
        )

        return CRYPTO

    context.user_data["cryptocurrency"] = crypto_map[
        update.message.text
    ]

    await update.message.reply_text(
        "💰 Enter the withdrawal amount in USD.\n\n"
        "Example:\n"
        "100",
        reply_markup=cancel_menu,
    )

    return AMOUNT

# ==========================================
# RECEIVE AMOUNT
# ==========================================

async def receive_amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message.text == "❌ Cancel":
        return await cancel(update, context)

    try:
        amount = float(update.message.text)

        if amount <= 0:
            raise ValueError

    except ValueError:

        await update.message.reply_text(
            "❌ Please enter a valid amount."
        )

        return AMOUNT

    # Minimum withdrawal
    if amount < 50:

        await update.message.reply_text(
            "❌ Minimum withdrawal is $50."
        )

        return AMOUNT

    balance = get_wallet_balance(
        update.effective_user.id
    )

    if balance < amount:

        await update.message.reply_text(
            f"❌ Insufficient wallet balance.\n\n"
            f"Available Balance: ${balance:,.2f}"
        )

        return AMOUNT

    context.user_data["amount"] = amount

    await update.message.reply_text(
        "📥 Enter your destination wallet address.",
        reply_markup=cancel_menu,
    )

    return ADDRESS

# ==========================================
# RECEIVE WALLET ADDRESS
# ==========================================

async def receive_address(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message.text == "❌ Cancel":
        return await cancel(update, context)

    wallet_address = update.message.text.strip()

    user_id = update.effective_user.id
    crypto = context.user_data["cryptocurrency"]
    amount = context.user_data["amount"]

    # Save withdrawal request
    create_withdrawal(
        user_id=user_id,
        cryptocurrency=crypto,
        wallet_address=wallet_address,
        amount=amount,
    )

    # Deduct wallet balance immediately
    admin_wallet_adjustment(
        user_id=user_id,
        amount=amount,
        transaction_type="Debit",
        reason="Withdrawal Request",
    )

    # Record transaction history
    record_wallet_transaction(
        user_id=user_id,
        transaction_type="Withdrawal",
        amount=amount,
        reason="Withdrawal Pending Approval",
    )

    # Notify user
    await update.message.reply_text(
        "✅ Withdrawal request submitted.\n\n"
        "Your request has been sent for review.\n"
        "Funds have been reserved from your wallet.\n\n"
        "You will be notified once an administrator reviews your request.",
        reply_markup=wallet_menu,
    )

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "💸 New Withdrawal Request\n\n"
            f"👤 User ID: {user_id}\n"
            f"🪙 Crypto: {crypto}\n"
            f"💵 Amount: ${amount:,.2f}\n\n"
            f"📥 Wallet Address:\n{wallet_address}"
        ),
    )

    context.user_data.pop("cryptocurrency", None)
    context.user_data.pop("amount", None)

    return ConversationHandler.END
    
# ==========================================
# CANCEL
# ==========================================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.pop("cryptocurrency", None)
    context.user_data.pop("amount", None)

    await update.message.reply_text(
        "Withdrawal cancelled.",
        reply_markup=wallet_menu,
    )

    return ConversationHandler.END
    
withdraw_handler = ConversationHandler(

    entry_points=[
        MessageHandler(
            filters.Regex("^💸 Withdraw Funds$"),
            withdraw,
        ),
    ],

    states={

        CRYPTO: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_crypto,
            ),
        ],

        AMOUNT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_amount,
            ),
        ],

        ADDRESS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_address,
            ),
        ],

    },

    fallbacks=[
        MessageHandler(
            filters.Regex("^❌ Cancel$"),
            cancel,
        ),
    ],

)
