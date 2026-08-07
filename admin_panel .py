from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from datetime import datetime

from config import ADMIN_ID
from keyboards import main_menu

from database import (
    get_pending_kyc,
    get_pending_deposits,
    update_deposit_status,
    get_deposit,
    add_wallet_balance,
    record_wallet_transaction,
    get_pending_refunds,
    update_refund_status,
    get_refund,
    get_referrer,
    has_first_deposit,
    mark_first_deposit,
    add_referral_bonus,
    increment_referrals,
    get_pending_withdrawals,
    get_withdrawal,
    update_withdrawal_status,
    admin_wallet_adjustment
)
    
admin_menu = ReplyKeyboardMarkup(
    [
        ["📥 Pending Deposits"],
        ["💸 Pending Withdrawals"],
        ["🪪 Pending KYC"],
        ["💰 Pending Refunds"],
        ["💳 Credit Wallet", "➖ Debit Wallet"],
        ["👥 Users", "📊 Statistics"],
        ["🏠 Main Menu"],
    ],
    resize_keyboard=True,
)

WITHDRAWAL_TXID = 0

async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Unauthorized.",
            reply_markup=main_menu,
        )

        return

    await update.message.reply_text(
        "🛠 *Admin Dashboard*\n\n"
        "Select an option below.",
        parse_mode="Markdown",
        reply_markup=admin_menu,
    )
    
async def pending_kyc(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.effective_user.id != ADMIN_ID:

        return

    kycs = get_pending_kyc()

    if not kycs:

        await update.message.reply_text(
            "✅ There are no pending KYC submissions."
        )

        return

    for kyc in kycs:

        user_id = kyc[0]
        full_name = kyc[1]
        id_document = kyc[2]
        selfie = kyc[3]

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Approve",
                        callback_data=f"approve_kyc:{user_id}",
                    ),
                    InlineKeyboardButton(
                        "❌ Reject",
                        callback_data=f"reject_kyc:{user_id}",
                    ),
                ]
            ]
        )

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=id_document,
            caption=(
                f"🪪 Pending KYC\n\n"
                f"👤 {full_name}\n"
                f"🆔 {user_id}\n\n"
                "📄 Identity Document"
            ),
            reply_markup=keyboard,
        )

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=selfie,
            caption="🤳 Selfie Holding Identity Document",
        )

async def pending_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    deposits = get_pending_deposits()

    if not deposits:
        await update.message.reply_text("No pending deposits.")
        return

    for deposit in deposits:

        deposit_id = deposit[0]
        user_id = deposit[1]
        network = deposit[2]
        amount = deposit[3]
        crypto_amount = deposit[4]
        txid = deposit[5]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Approve",
                    callback_data=f"approve_deposit:{deposit_id}",
                ),
                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=f"reject_deposit:{deposit_id}",
                ),
            ]
        ])

        await update.message.reply_text(
            f"📥 *Pending Deposit*\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"🌐 Network: {network}\n"
            f"💵 USD: ${amount:,.2f}\n"
            f"🪙 Crypto: {crypto_amount}\n\n"
            f"🔗 TXID:\n`{txid}`",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

async def pending_refunds(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    refunds = get_pending_refunds()

    if not refunds:
        await update.message.reply_text("No pending refunds.")
        return

    for refund in refunds:

        refund_id = refund[0]
        user_id = refund[1]
        full_name = refund[2]
        investment_amount = refund[5]
        cryptocurrency = refund[6]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Approve",
                    callback_data=f"approve_refund:{refund_id}",
                ),
                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=f"reject_refund:{refund_id}",
                ),
            ]
        ])

        await update.message.reply_text(
            f"💰 *Pending Refund*\n\n"
            f"👤 {full_name}\n"
            f"🆔 User ID: `{user_id}`\n"
            f"💵 Amount: {investment_amount}\n"
            f"🪙 Crypto: {cryptocurrency}",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        
# =====================================
# PENDING WITHDRAWALS
# =====================================

async def pending_withdrawals(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.effective_user.id != ADMIN_ID:
        return

    withdrawals = get_pending_withdrawals()

    if not withdrawals:

        await update.message.reply_text(
            "✅ No pending withdrawal requests."
        )

        return

    for withdrawal in withdrawals:

        withdrawal_id = withdrawal[0]
        user_id = withdrawal[1]
        cryptocurrency = withdrawal[2]
        wallet_address = withdrawal[3]
        amount = withdrawal[4]

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Approve",
                        callback_data=f"approve_withdrawal:{withdrawal_id}",
                    ),
                    InlineKeyboardButton(
                        "❌ Reject",
                        callback_data=f"reject_withdrawal:{withdrawal_id}",
                    ),
                ]
            ]
        )

        await update.message.reply_text(
            f"💸 *Pending Withdrawal*\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"🪙 Cryptocurrency: {cryptocurrency}\n"
            f"💵 Amount: ${amount:,.2f}\n\n"
            f"📥 Wallet Address:\n"
            f"`{wallet_address}`",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

async def deposit_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    action, deposit_id = query.data.split(":")
    deposit_id = int(deposit_id)

    if action == "approve_deposit":

        update_deposit_status(deposit_id, "Approved")

        # Get deposit details
        user_id, amount = get_deposit(deposit_id)

        # Credit investor's wallet
        add_wallet_balance(user_id, amount)

        record_wallet_transaction(
            user_id=user_id,
            transaction_type="Deposit",
            amount=amount,
            reason="Crypto Deposit Approved",
        )

        # =====================================
        # PAY FIRST DEPOSIT REFERRAL BONUS (10%)
        # =====================================

        if not has_first_deposit(user_id):

            mark_first_deposit(user_id)

            referrer_id = get_referrer(user_id)

            if referrer_id:

                increment_referrals(referrer_id)

                # 10% of first approved deposit
                bonus = round(amount * 0.10, 2)

                add_referral_bonus(
                    referrer_id,
                    bonus,
                )

                record_wallet_transaction(
                    user_id=referrer_id,
                    transaction_type="Referral Bonus",
                    amount=bonus,
                    reason="10% First Deposit Referral Bonus",
                )

                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        "🎉 *Referral Bonus Earned!*\n\n"
                        "One of your direct referrals has completed their first verified deposit.\n\n"
                        f"💰 Bonus Earned: *${bonus:,.2f}*\n\n"
                        "The bonus has been credited to your Affiliate Balance.\n\n"
                        "⚠️ Referral bonuses cannot be withdrawn immediately.\n"
                        "They must first be used to purchase Cloud Mining hash power."
                    ),
                    parse_mode="Markdown",
                )

        # Notify the investor
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ Your deposit of ${amount:,.2f} has been approved.\n\n"
                "The funds have been added to your wallet."
            ),
        )

        await query.edit_message_text(
            "✅ Deposit Approved"
        )

    elif action == "reject_deposit":

        update_deposit_status(deposit_id, "Rejected")

        user_id, amount = get_deposit(deposit_id)

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ Your deposit of ${amount:,.2f} has been rejected."
            ),
        )

        await query.edit_message_text(
            "❌ Deposit Rejected"
        )

async def refund_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    action, refund_id = query.data.split(":")
    refund_id = int(refund_id)

    user_id, amount = get_refund(refund_id)

    amount = float(
        str(amount).replace("$", "").replace(",", "").strip()
    )

    if action == "approve_refund":

        update_refund_status(refund_id, "Approved")

        add_wallet_balance(user_id, amount)
        record_wallet_transaction(
            user_id=user_id,
            transaction_type="Refund",
            amount=amount,
            reason="Refund Approved",
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ Your refund request has been approved.\n\n"
                f"${amount:,.2f} has been added to your wallet."
            ),
        )

        await query.edit_message_text(
            "✅ Refund Approved"
        )

    elif action == "reject_refund":

        update_refund_status(refund_id, "Rejected")

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Your refund request has been rejected."
            ),
        )

        await query.edit_message_text(
            "❌ Refund Rejected"
        )

# =====================================
# WITHDRAWAL CALLBACK
# =====================================

async def withdrawal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query
    await query.answer()

    action, withdrawal_id = query.data.split(":")
    withdrawal_id = int(withdrawal_id)

    user_id, amount, cryptocurrency, wallet_address = get_withdrawal(
        withdrawal_id
    )

    # ---------------- APPROVE ----------------

    if action == "approve_withdrawal":

        context.user_data["withdrawal_id"] = withdrawal_id

        await query.message.reply_text(
            "📤 Paste the blockchain Transaction Hash (TXID).\n\n"
            "Example:\n\n"
            "5f94cb65ad77f4d7..."
        )

        return WITHDRAWAL_TXID

    # ---------------- REJECT ----------------

    elif action == "reject_withdrawal":

        reason = "Withdrawal rejected by administrator."

        update_withdrawal_status(
            withdrawal_id,
            "Rejected",
            reason,
        )

        admin_wallet_adjustment(
            user_id=user_id,
            amount=amount,
            transaction_type="Credit",
            reason="Rejected Withdrawal Refund",
        )

        record_wallet_transaction(
            user_id=user_id,
            transaction_type="Withdrawal",
            amount=amount,
            reason="Withdrawal Rejected (Refunded)",
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Your withdrawal request has been rejected.\n\n"
                f"Reason:\n{reason}\n\n"
                "The amount has been returned to your wallet."
            ),
        )

        await query.edit_message_text(
            "❌ Withdrawal Rejected"
        )

        return ConversationHandler.END
        
# =====================================
# RECEIVE WITHDRAWAL TXID
# =====================================

async def receive_withdrawal_txid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    txid = update.message.text.strip()

    withdrawal_id = context.user_data["withdrawal_id"]

    user_id, amount, cryptocurrency, wallet_address = get_withdrawal(
        withdrawal_id
    )

    update_withdrawal_status(
        withdrawal_id=withdrawal_id,
        status="Approved",
        txid=txid,
        completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    record_wallet_transaction(
        user_id=user_id,
        transaction_type="Withdrawal",
        amount=amount,
        reason="Withdrawal Approved",
    )

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "✅ Withdrawal Completed\n\n"
            f"💵 Amount: ${amount:,.2f}\n"
            f"🪙 Network: {cryptocurrency}\n\n"
            f"📥 Destination Wallet:\n"
            f"{wallet_address}\n\n"
            f"🔗 Transaction Hash:\n"
            f"{txid}\n\n"
            "Your withdrawal has been broadcast to the blockchain.\n\n"
            "Network confirmations may take a few minutes."
        ),
    )

    await update.message.reply_text(
        "✅ Withdrawal completed successfully."
    )

    context.user_data.clear()

    return ConversationHandler.END

# =====================================
# HANDLERS
# =====================================

admin_panel_handler = MessageHandler(
    filters.Regex("^🛠 Admin Panel$"),
    admin_panel,
)

pending_kyc_handler = MessageHandler(
    filters.Regex("^🪪 Pending KYC$"),
    pending_kyc,
)

pending_deposits_handler = MessageHandler(
    filters.Regex("^📥 Pending Deposits$"),
    pending_deposits,
)

pending_withdrawals_handler = MessageHandler(
    filters.Regex("^💸 Pending Withdrawals$"),
    pending_withdrawals,
)

pending_refunds_handler = MessageHandler(
    filters.Regex("^💰 Pending Refunds$"),
    pending_refunds,
)

deposit_callback_handler = CallbackQueryHandler(
    deposit_callback,
    pattern="^(approve_deposit|reject_deposit):",
)

refund_callback_handler = CallbackQueryHandler(
    refund_callback,
    pattern="^(approve_refund|reject_refund):",
)

withdrawal_handler = ConversationHandler(

    entry_points=[
        CallbackQueryHandler(
            withdrawal_callback,
            pattern="^(approve_withdrawal|reject_withdrawal):",
        )
    ],

    states={
        WITHDRAWAL_TXID: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_withdrawal_txid,
            )
        ]
    },

    fallbacks=[],
)
