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

# ❗ ОБЯЗАТЕЛЬНО chat_id, не username
OPERATOR_CHAT_ID = 530982753  # ← вставь сюда ID оператора
OPERATOR_USERNAME = "@olya_so1"

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
            "step": "start",
            "country": None,
            "amount": None,
        }

# ---------- ХЕНДЛЕРЫ ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    users[user_id]["step"] = "country"

    await update.message.reply_text(
        "Здравствуйте 👋\n\n"
        "Здесь вы можете безопасно и удобно обменять валюту в Азии 💱\n\n"
        "Мы работаем с туристами и экспатами по всему миру и помогаем получать деньги "
        "быстро, без лишних рисков и сложных схем 🌏\n\n"
        "Выберите страну, где вы сейчас, или нужную услугу 👇",
        reply_markup=MAIN_KEYBOARD,
    )

async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    text = update.message.text
    if text not in COUNTRY_OPTIONS:
        return

    users[user_id]["country"] = text
    users[user_id]["step"] = "amount"

    await update.message.reply_text(
        "Введите сумму, которую хотите обменять.\n\n"
        "Можно написать в любой валюте:\n"
        "например: 1000 USD / 3000 USDT / 150 000 RUB"
    )

async def amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    if users[user_id]["step"] != "amount":
        return

    users[user_id]["amount"] = update.message.text
    users[user_id]["step"] = "country"

    # -------- уведомление оператору --------
    user = update.effective_user
    message_to_operator = (
        "📩 НОВАЯ ЗАЯВКА\n\n"
        f"👤 Пользователь: @{user.username or 'без username'}\n"
        f"🆔 ID: {user.id}\n"
        f"🌍 Страна: {users[user_id]['country']}\n"
        f"💰 Сумма: {users[user_id]['amount']}"
    )

    await context.bot.send_message(
        chat_id=OPERATOR_CHAT_ID,
        text=message_to_operator,
    )

    # -------- ответ клиенту --------
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