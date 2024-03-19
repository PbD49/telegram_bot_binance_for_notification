import telebot
import sqlite3
import requests
import time
from token_bot_and_id_chat import token, chat_id
import json


bot = telebot.TeleBot(token)


def get_price_dollar(symbols_dollars):
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()

    for symbol in symbols_dollars:
        symbol_usd = symbol + 'USDT'
        url_usd = 'https://api.binance.com/api/v3/ticker/price?symbol=' + symbol_usd
        data_usd = requests.get(url_usd).json()
        if 'price' in data_usd:
            price_usd = data_usd['price']
            cur.execute('UPDATE parser_usd SET price_usd = ? WHERE symbol_usd = ?', (price_usd, symbol))
            conn.commit()
        time.sleep(0.3)


def get_task_dollar():
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM parser_usd')
    results = cur.fetchall()
    for ticker in results:
        current_ticker = ticker[2]
        current_price_usd = ticker[1]

        query = ('''
            SELECT * FROM task_usd 
            WHERE symbol_usd = :current_ticker 
            AND (amount_usd <= :current_price_usd AND task_type_usd = 1)
            OR (amount_usd >= :current_price_usd AND task_type_usd = 2)
        ''')
        cur.execute(query, (current_ticker, current_price_usd))

        cur.execute(query, {"current_ticker": current_ticker, "current_price_usd": current_price_usd})
        for task in cur.fetchall():
            # user_id = message.chat.id
            bot.send_message(chat_id=task[1], text=f'Просыпайся!  🛎🔊🔔📣📢  {task[2]} достиг уровня задания {task[3]} USD')
            cur.execute(f'DELETE FROM task_usd WHERE id = {task[0]}')
            conn.commit()
            #print(task[1])
        print(current_price_usd)

    cur.close()
    conn.close()


symbols_dollar = ['BTC', 'BNB', 'ETH']


while True:
    get_price_dollar(symbols_dollar)
    get_task_dollar()
