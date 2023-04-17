import telebot
from telebot import types
from pages_parser import Parent

bot = telebot.TeleBot("TOKEN")

@bot.message_handler(commands=['start'])
def start(message):
    msg = f'Привет, {message.from_user.first_name}! Что бы ты хотел найти?'
    bot.send_message(message.chat.id, msg, parse_mode='html')

@bot.message_handler()
def search(message):
    text = message.text
    item = Parent(text)
    if item.get_img():
        bot.send_photo(message.chat.id, item.get_img(), parse_mode='html')
    for block in item.get_blocks():
        if block:
            bot.send_message(message.chat.id, block, parse_mode='html') 


if __name__ == "__main__":
    bot.polling(non_stop=True)
