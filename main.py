import telebot
from telebot import types
import db_operations as db
import time
from decimal import Decimal

API_TOKEN = '7465282044:AAF3N30I7AHad8zHeOp5EAxXRA934yxqZoM'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_main_menu(message)


def send_main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    menu_btn = types.KeyboardButton('📋 Меню')
    update_product_btn = types.KeyboardButton('🔄 Обновить продукт')
    list_product_btn = types.KeyboardButton('🤢 Список продуктов')
    markup.add(menu_btn, update_product_btn, list_product_btn)
    bot.send_message(message.chat.id, "Добро пожаловать в кофейню! Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '📋 Меню')
def send_menu(message):
    menu = db.get_menu()
    response = "Меню:\n"
    for item in menu:
        response += f"{item['dish_title']} - {item['dish_desc']} (Цена: {item['cost']} руб)\nРецепт: {item['steps']}\n\n"
    markup = types.ReplyKeyboardMarkup(row_width=1)
    back_btn = types.KeyboardButton('⬅️ Назад')
    markup.add(back_btn)
    bot.send_message(message.chat.id, response, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🔄 Обновить продукт')
def update_product(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    back_btn = types.KeyboardButton('⬅️ Назад')
    markup.add(back_btn)
    bot.send_message(message.chat.id, "Введите через пробел ID продукта и новое количество (например, '3 25'):",
                     reply_markup=markup)
    bot.register_next_step_handler(message, process_update_product)

@bot.message_handler(func=lambda message: message.text == '🤢 Список продуктов')
def list_products(message):
    products = db.get_products()
    response = "Список продуктов:\n"
    for product in products:
        response += f"ID: {product['id_product']}, Название: {product['title']}, Количество: {product['count_kg']} кг\n"
    markup = types.ReplyKeyboardMarkup(row_width=1)
    back_btn = types.KeyboardButton('⬅️ Назад')
    markup.add(back_btn)
    bot.send_message(message.chat.id, response, reply_markup=markup)
def process_update_product(message):

    if message.text != '⬅️ Назад':
        try:

            data = message.text.split()
            product_id = int(data[0])
            count = Decimal(data[1])

            current_product = db.get_product(product_id)
            if current_product is None:
                bot.send_message(message.chat.id, "Продукт не найден.")
                return

            current_count = Decimal(current_product['count_kg'])
            new_count = current_count + count
            db.update_product_count(product_id, new_count)

            action_text = ""
            if count > 0:
                action_text = "увеличено"
            elif count < 0:
                action_text = "уменьшено"
            else:
                action_text = "установлено"

            bot.send_message(message.chat.id,
                           f"Количество продукта {current_product['title']} успешно {action_text} до {new_count} кг")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {e}")
    send_main_menu(message)

@bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
def go_back(message):
    send_main_menu(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("update_product_"))
def handle_product_update(call):
    product_id = int(call.data.split("_")[2])
    msg = bot.send_message(call.message.chat.id,
                           f"Введите новое количество продукта {db.get_product(product_id)['title']}:")
    bot.register_next_step_handler(msg, lambda m: process_product_action(m, product_id))


def process_product_action(message, product_id):
    try:
        count = Decimal(message.text)
        current_product = db.get_product(product_id)
        if current_product is None:
            bot.send_message(message.chat.id, "Продукт не найден.")
            return
        current_count = Decimal(current_product['count_kg'])
        new_count = current_count + count
        db.update_product_count(product_id, new_count)
        bot.send_message(message.chat.id,
                         f"Количество продукта обновлено: {current_product['title']}, новое количество {new_count} кг")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def notify_new_order(order):
    clients = db.get_clients()
    for client in clients:
        bot.send_message(client['telegram_id'], "Новый заказ!")


def check_new_orders():
    last_order_id = 0
    while True:
        orders = db.get_orders()
        new_orders = [order for order in orders if order['id_order'] > last_order_id]
        for order in new_orders:
            notify_new_order(order)
        if new_orders:
            last_order_id = new_orders[-1]['id_order']
        time.sleep(10)


if __name__ == '__main__':
    import threading

    threading.Thread(target=check_new_orders).start()
    bot.polling()
