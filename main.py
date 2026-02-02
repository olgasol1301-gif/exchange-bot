import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен ТОЛЬКО из Railway
OPERATOR_USERNAME = "@YOUR_USERNAME"  # <-- замени на свой юзернейм

# ================== ХРАНЕНИЕ СОСТОЯНИЯ ==================

users = {}

def ensure_user(user_id: int):
    if user_id not in users:
        users[user_id] = {
            "returning": False,
            "country": None,
            "amount": None,
        }

# ================== КНОПКИ ==================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🇱🇰 Шри-Ланка", "🇻🇳 Вьетнам"],
        ["🇹🇭 Тайланд"],
        ["💳 Alipay / WeChat"],
        ["🌍 Другая страна", "🧑‍💼 Связь с оператором"],
    ],
    resize_keyboard=True,
)

BACK_KEYBOARD = ReplyKeyboardMarkup(
    [["🔁 Выбрать другую страну"]],
    resize_keyboard=True,
)

OPERATOR_KEYBOARD = ReplyKeyboardMarkup(
    [["🧑‍💼 Написать оператору"]],
    resize_keyboard=True,
)

COUNTRY_OPTIONS = [
    "🇱🇰 Шри-Ланка",
    "🇻🇳 Вьетнам",
    "🇹🇭 Тайланд",
    "💳 Alipay / WeChat",
    "🌍 Другая страна",
]

# ================== ХЕНДЛЕРЫ ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    if users[user_id]["returning"]:
        text = (
            "С возвращением 👋\n\n"
            "Рады снова помочь с обменом валюты 💱\n"
            "Выберите страну или нужную услугу 👇"
        )
    else:
        users[user_id]["returning"] = True
        text = (
            "Здравствуйте 👋\n\n"
            "Здесь вы можете безопасно и удобно обменять валюту в Азии 💱\n\n"
            "Мы работаем с туристами и экспатами по всему миру и помогаем получать деньги "
            "быстро, без лишних рисков и сложных схем 🌏\n\n"
            "Выберите страну, где вы сейчас, или нужную услугу 👇"
        )

    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD)


async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    text = update.message.text

    if text not in COUNTRY_OPTIONS:
        return

    users[user_id]["country"] = text
    users[user_id]["amount"] = None

    await update.message.reply_text(
        "Введите сумму, которую хотите обменять.\n\n"
        "Можно написать в любой валюте:\n"
        "например: 1000 USD / 3000 USDT / 150 000 RUB",
        reply_markup=BACK_KEYBOARD,
    )


async def amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    # если страна не выбрана — НЕ принимаем текст как заявку
    if users[user_id]["country"] is None:
        await update.message.reply_text(
            "Пожалуйста, сначала выберите страну 👇",
            reply_markup=MAIN_KEYBOARD,
        )
        return

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
        reply_markup=OPERATOR_KEYBOARD,
    )


async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    users[user_id]["country"] = None
    users[user_id]["amount"] = None

    await start(update, context)


async def contact_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Напишите оператору напрямую: {OPERATOR_USERNAME}"
    )

# ================== ЗАПУСК ==================

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не найден в переменных окружения")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.Regex("^🔁"), back_to_start))
    app.add_handler(MessageHandler(filters.Regex("^🧑‍💼"), contact_operator))

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("🇱🇰|🇻🇳|🇹🇭|💳|🌍"),
            country_selected,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            amount_received,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()