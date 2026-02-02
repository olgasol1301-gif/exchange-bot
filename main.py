from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPERATOR_USERNAME = "@YOUR_OPERATOR_USERNAME"  # ← замени

users = {}

# ---------- КНОПКИ ----------

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🇱🇰 Шри-Ланка", "🇻🇳 Вьетнам"],
        ["🇹🇭 Тайланд"],
        ["💳 Alipay / WeChat"],
        ["🌍 Другая страна", "🧑‍💼 Связь с оператором"],
    ],
    resize_keyboard=True,
)

AFTER_REQUEST_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🔁 Выбрать другую страну"],
        ["🧑‍💼 Написать оператору"],
    ],
    resize_keyboard=True,
)

COUNTRY_OPTIONS = [
    "🇱🇰 Шри-Ланка",
    "🇻🇳 Вьетнам",
    "🇹🇭 Тайланд",
    "💳 Alipay / WeChat",
    "🌍 Другая страна",
]

# ---------- ВСПОМОГАТЕЛЬНОЕ ----------

def ensure_user(user_id: int):
    if user_id not in users:
        users[user_id] = {
            "step": "start",  # start → country → amount
        }

# ---------- ХЕНДЛЕРЫ ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    users[user_id]["step"] = "country"

    await update.message.reply_text(
        "Здравствуйте 👋\n\n"
        "Здесь вы можете безопасно и удобно обменять валюту в Азии 💱\n\n"
        "Выберите страну или услугу 👇",
        reply_markup=MAIN_KEYBOARD,
    )

async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    if update.message.text not in COUNTRY_OPTIONS:
        return

    users[user_id]["step"] = "amount"

    await update.message.reply_text(
        "Введите сумму, которую хотите обменять.\n\n"
        "Например: 1000 USD / 3000 USDT / 150 000 RUB"
    )

async def amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    if users[user_id]["step"] != "amount":
        return

    users[user_id]["step"] = "country"  # ❗ сразу разрешаем новый выбор

    await update.message.reply_text(
        "Отлично 👍\n"
        "Заявка передана оператору.\n\n"
        "Он напишет вам для уточнения деталей.",
        reply_markup=AFTER_REQUEST_KEYBOARD,
    )

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def contact_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Напишите оператору напрямую: {OPERATOR_USERNAME}"
    )

# ---------- ЗАПУСК ----------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^🔁"), back_to_start))
    app.add_handler(MessageHandler(filters.Regex("^🧑‍💼"), contact_operator))
    app.add_handler(MessageHandler(filters.Regex("🇱🇰|🇻🇳|🇹🇭|💳|🌍"), country_selected))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amount_received))

    app.run_polling()

if __name__ == "__main__":
    main()