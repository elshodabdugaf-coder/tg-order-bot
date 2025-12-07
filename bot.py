from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Admin ID
ADMIN_ID = 1158104253
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Men @italics_shop kanalini botiman.\n"
        "Menga yoqtirgan kiyimingizni rasm bilan yuboring."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_file_id = update.message.photo[-1].file_id
    user_data[user_id] = {"photo": photo_file_id}
    await update.message.reply_text("Rasm qabul qilindi. Iltimos, o‘lchamni kiriting.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id in user_data and "size" not in user_data[user_id]:
        # O'lcham kiritildi
        user_data[user_id]["size"] = text

        # Adminga rasm + o'lcham yuborish
        keyboard = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton("Narx kiriting", callback_data=f"ask_price_{user_id}")
        )
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=user_data[user_id]["photo"],
            caption=f"Foydalanuvchi @{update.message.from_user.username} rasm yubordi.\nO‘lcham: {text}",
            reply_markup=keyboard
        )
        await update.message.reply_text("O‘lcham qabul qilindi, admin tekshiradi. Narx kirish tugmasi adminda.")
    else:
        await update.message.reply_text("Avval rasm yuboring.")

# Tugma bosilganda callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("ask_price_") and query.from_user.id == ADMIN_ID:
        target_user_id = int(data.split("_")[2])
        user_data["await_price"] = target_user_id
        await query.message.reply_text("Iltimos, narxni kiriting:")

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "await_price" not in user_data:
        return

    target_user_id = user_data["await_price"]
    price = update.message.text
    user_data[target_user_id]["price"] = price
    del user_data["await_price"]

    # Foydalanuvchiga narx yuborish va Xarid tugmasi
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton("Xarid qilish", callback_data=f"buy_{price}")
    )
    await context.bot.send_message(
        chat_id=target_user_id,
        text=f"Narx = {price}",
        reply_markup=keyboard
    )

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("buy_"):
        price = data.split("_")[1]
        await query.message.reply_text(
            f"To‘lovni 5614681904254459 Elshodbek Abdug'afforov kartaga qiling va chekni botga yuboring.\nNarx: {price}"
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token("SIZNING_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_price_input))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="ask_price_"))
    app.add_handler(CallbackQueryHandler(buy_handler, pattern="buy_"))

    print("Bot ishga tushdi...")
    app.run_polling()