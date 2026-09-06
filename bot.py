import os
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # Токен из переменных окружения
PRODUCT_URL = "https://zhukovid71-design.github.io/zarplata-lokbrig/"  # Ваша ссылка

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- КОМАНДА /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Открыть калькулятор", url=PRODUCT_URL))
    bot.send_message(
        message.chat.id,
        "🚂 Добро пожаловать!\n\n"
        "💰 Стоимость доступа: 350 Telegram Stars.\n"
        "👉 Нажмите /buy, чтобы начать покупку.",
        reply_markup=markup
    )

# --- КОМАНДА /buy ---
@bot.message_handler(commands=['buy'])
def handle_buy(message):
    # Отправляем инвойс (счёт) на оплату в Telegram Stars
    bot.send_invoice(
        chat_id=message.chat.id,
        title="Доступ к калькулятору",
        description="Полная версия калькулятора зарплаты с отчётом",
        invoice_payload="access_to_calculator",
        provider_token="",  # Для Stars оставляем пустым
        currency="XTR",     # XTR = Telegram Stars
        prices=[{"label": "Доступ", "amount": 350}],  # 350 Stars
        start_parameter="buy_calculator",
        need_shipping_address=False,
        is_flexible=False
    )

# --- ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА ---
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

# --- УСПЕШНАЯ ОПЛАТА ---
@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Открыть калькулятор", url=PRODUCT_URL))
    bot.send_message(
        message.chat.id,
        f"✅ Оплата прошла успешно!\n\n"
        f"🎁 Ваша ссылка для доступа:\n{PRODUCT_URL}\n\n"
        f"Сохраните её или нажмите кнопку:",
        reply_markup=markup
    )

# --- ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке (для работы с Flask)
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    # Запускаем Flask (для Render)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))