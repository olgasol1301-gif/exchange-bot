print("MAIN.PY STARTED")

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPERATOR_USERNAME = "@olya_so1"

users = {}  # user_id: {"returning": True, "country": None, "amount": None}

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🇱🇰 Шри-Ланка", "🇻🇳 Вьетнам"],
        ["🇹🇭 Тайланд"],
        ["💳 Alipay / WeChat"],
        ["🌍 Другая страна", "🧑‍💼 Связь с оператором"]
    ],
    resize_keyboard=True
)
def ensure_user(user_id):
    if user_id not in users:
        users[user_id] = {}
        
def is_returning(user_id):
    return user_id in users

async def start(update, context):
    user_id = update.effective_user.id
    ensure_user(user_id)

    if is_returning(user_id):
        text = (
            "С возвращением 👋\n\n"
            "Рады снова помочь с обменом валюты 💱\n"
            "Выберите страну или нужную услугу 👇"
        )
    else:
        users[user_id] = {"returning": True}
        text = (
            "Здравствуйте 👋\n\n"
            "Здесь вы можете безопасно и удобно обменять валюту в Азии 💱\n\n"
            "Мы работаем с туристами и экспатами по всему миру и помогаем получать деньги "
            "быстро, без лишних рисков и сложных схем 🌏\n\n"
            "Выберите страну, где вы сейчас, или нужную услугу 👇"
        )

    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD)

async def country_selected(update, context):
    user_id = update.effective_user.id
    ensure_user(user_id)
    users[user_id]["country"] = update.message.text

    await update.message.reply_text(
        "Введите сумму, которую хотите обменять.\n\n"
        "Можно написать в любой валюте:\n"
        "например: 1000 USD / 3000 USDT / 150 000 RUB",
        reply_markup=ReplyKeyboardMarkup([["🔁 Выбрать другую страну"]], resize_keyboard=True)
    )

async def amount_received(update, context):
    user_id = update.effective_user.id
    ensure_user(user_id)
    users[user_id]["amount"] = update.message.text

    await update.message.reply_text(
        "Отлично 👍\n"
        "Мы передали заявку оператору.\n\n"
        "Он напишет вам и уточнит детали:\n"
        "курс, способ получения и время."
    )

    await update.message.reply_text(
        f"❗️Важно\n\n"
        f"С вами работает только один официальный оператор сервиса — {OPERATOR_USERNAME}\n\n"
        f"Если вам пишут с других аккаунтов — это мошенники.",
        reply_markup=ReplyKeyboardMarkup([[ "🧑‍💼 Написать оператору" ]], resize_keyboard=True)
    )

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("🇱🇰|🇻🇳|🇹🇭"), country_selected))
    app.add_handler(MessageHandler(filters.Regex("🔁"), back_to_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amount_received))

    app.run_polling()

if __name__ == "__main__":
    main()