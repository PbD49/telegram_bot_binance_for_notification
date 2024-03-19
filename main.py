import telebot
from telebot import types
import json
from token_bot_and_id_chat import chat_id, token
from urllib import response
from base_db import DataBase
import requests
import time


class StartBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)

        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            text = '🥷 Здарова, Уважаемый! Устроим засаду ? 🥷'
            self.send_message_with_buttons(message, text)

    def send_message_with_buttons(self, message, text):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Посмотреть курс валютных пар')
        keyboard.add('Посмотреть список заданий')
        keyboard.add('Написать новое задание')
        keyboard.add('Удалить задание')
        self.bot.send_message(message.chat.id, text, reply_markup=keyboard)


class ViewListOfTasks(StartBot):
    def __init__(self, token):
        super().__init__(token)
        self.db = DataBase('db.db')

        @self.bot.message_handler(func=lambda message: message.text == 'Посмотреть список заданий')
        def callback(message):
            user_id = message.from_user.id
            task_usd = self.db.fetch_all(f"SELECT * FROM task_usd WHERE user_id = {user_id}")

            if len(task_usd) == 0:
                self.bot.send_message(message.from_user.id, 'На данный момент список заданий пуст 📭')
            else:
                for t, task in enumerate(task_usd, start=1):
                    task_name = task[2]
                    task_amount = task[3]
                    self.bot.send_message(message.from_user.id, f'{t}. 🎲 {task_name} ↔️ {task_amount}')


class WriteANewAssignment(StartBot):
    def __init__(self, token):
        super().__init__(token)
        self.db = DataBase('db.db')

        @self.bot.message_handler(func=lambda message: message.text == 'Написать новое задание')
        def new1_task_handler(message):
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('BNB', 'ETH', 'BTC')
            keyboard.add('Назад')
            self.bot.send_message(message.chat.id, 'Выберите валютную пару:', reply_markup=keyboard)

        @self.bot.message_handler(func=lambda message: message.text == 'Назад')
        def back_btn(message):
            text = 'Вы вернулись в главное меню:'
            self.send_stop(message, text)

        @self.bot.message_handler(
            func=lambda message: message.text == 'BNB' or message.text == 'ETH' or message.text == 'BTC')
        def symbol_chosen_handler(message):
            self.set_task_symbol_dollar(message)

    def send_stop(self, message, text):
        self.send_message_with_buttons(message, text)

    # Обработчик выбора валютной пары
    def set_task_symbol_dollar(self, message):
        # Запоминаем выбранную валютную пару
        user_data = {'symbol': message.text}

        self.bot.send_message(message.chat.id, 'Введите стоимость:', reply_markup=telebot.types.ReplyKeyboardRemove())
        self.bot.register_next_step_handler(message, self.set_task_amount_dollar, user_data)

    # Обработчик ввода стоимости нового задания
    def set_task_amount_dollar(self, message, user_data):
        try:
            # Пробуем преобразовать введенное значение в число
            amount = float(message.text)
            user_data['amount_usd'] = amount
            user_id = message.chat.id
            parser_usd = self.db.fetch_one('SELECT * FROM parser_usd')
            prices = parser_usd[1]

            # task_type = 1
            # task_type = 2
            # Теперь переменная task_type = 1,
            # если введенная сумма задания пользователя больше или равна, чем цена стоимости торговой площадки, и tak_type = 2,
            # если введенная сумма задания пользователя больше меньше, чем цена стоимости торговой площадки
            task_type = 1
            if amount <= float(prices):
                task_type = 2
                print(amount)

            self.db.execute_query(
                'INSERT INTO task_usd(user_id, symbol_usd, amount_usd, task_type_usd) VALUES(?, ?, ?, ?)',
                (user_id, user_data['symbol'], amount, task_type))
            self.send_stop(message, f'Новое задание добавлено:  {user_data["symbol"]} {user_data["amount_usd"]}')
        except ValueError:
            text = 'Неверный формат числа, попробуйте еще раз.'
            self.send_stop(message, text)


class DeleteTasks(StartBot):
    def __init__(self, token):
        super().__init__(token)
        self.db = DataBase('db.db')

        @self.bot.message_handler(func=lambda message: message.text == "Удалить задание")
        def menu_delete_task(message):
            user_id = message.from_user.id
            task_usd = self.db.fetch_all(f"SELECT * FROM task_usd WHERE user_id = {user_id}")
            if len(task_usd) == 0:
                self.bot.send_message(message.from_user.id, 'На данный момент список заданий пуст 📭')
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                for t, task in enumerate(task_usd, start=1):
                    task_name = task[2]
                    task_amount = task[3]
                    task_id = task[0]
                    btn_text = f'{t}. {task_name} 🗑 {task_amount}'
                    btn = types.InlineKeyboardButton(text=btn_text, callback_data=f'delete_task_{task_id}')
                    markup.add(btn)
                reply = "Выбери задание и нажми, чтобы удалить его."
                self.bot.send_message(message.from_user.id, reply, reply_markup=markup)

                @self.bot.callback_query_handler(func=lambda call: call.data.startswith('delete_task'))
                def delete_task(call):
                    user_id = call.from_user.id
                    task_id = call.data.split('_')[2]

                    self.db.execute_query(f"DELETE FROM task_usd WHERE  user_id = {user_id} AND id = {task_id}")

                    user_id = call.from_user.id
                    task_id = call.data.split('_')[2]
                    # bot.answer_callback_query(callback_query_id=call.id, text="Задание удалено!")
                    self.bot.send_message(user_id, "Задание удалено!")


class ViewTheExchangeRateOfCurrencyPairs(StartBot):
    def __init__(self, token):
        super().__init__(token)

        @self.bot.message_handler(func=lambda message: message.text == "Посмотреть курс валютных пар")
        def view_the_exchange_rate_of_currency_pairs(message):
            symbols_dollars = ['BTC', 'BNB', 'ETH']
            response = "Курсы валютных пар:\n\n"
            for symbol in symbols_dollars:
                symbol_usd = symbol + 'USDT'
                url_usd = 'https://api.binance.com/api/v3/ticker/price?symbol=' + symbol_usd
                data_usd = requests.get(url_usd).json()
                if 'price' in data_usd:
                    price_usd = data_usd['price']
                    response += f"{symbol} | USD: {price_usd}\n"
            keyboard = types.InlineKeyboardMarkup()
            refresh_button = types.InlineKeyboardButton("Обновить", callback_data='refresh')
            keyboard.add(refresh_button)
            self.bot.send_message(message.chat.id, f'{response}', reply_markup=keyboard)
            time.sleep(1)

        @self.bot.callback_query_handler(func=lambda call: call.data == 'refresh')
        def refresh_exchange_rates(call):
            response = "Курсы валютных пар:\n\n"
            symbols_dollars = ['BTC', 'BNB', 'ETH']
            for symbol in symbols_dollars:
                symbol_usd = symbol + 'USDT'
                url_usd = 'https://api.binance.com/api/v3/ticker/price?symbol=' + symbol_usd
                data_usd = requests.get(url_usd).json()
                if 'price' in data_usd:
                    price_usd = data_usd['price']
                    response += f"{symbol} | USD: {price_usd}\n"
            keyboard = types.InlineKeyboardMarkup()
            refresh_button = types.InlineKeyboardButton("Обновить", callback_data='refresh')
            keyboard.add(refresh_button)
            self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=f'{response}', reply_markup=keyboard)
            time.sleep(0.1)


class BotRunner(ViewListOfTasks, WriteANewAssignment, DeleteTasks, ViewTheExchangeRateOfCurrencyPairs, StartBot):
    def __init__(self, token):
        super().__init__(token)

    def run(self):
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as e:
                print(f"Ошибка: {e}")
                continue


bot = BotRunner(token)
bot.run()
