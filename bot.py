import telebot
from telebot import types
from pages_parser import Page

bot = telebot.TeleBot("TOKEN")

@bot.message_handler(commands=['start'])
def start(message):
    msg = f'Привет, {message.from_user.first_name}! Что бы ты хотел найти?'
    bot.send_message(message.chat.id, msg, parse_mode='html')

@bot.message_handler()
def search(message):
    text = message.text
    item = Page(text)
    if item.get_img():
        bot.send_photo(message.chat.id, item.get_img(), parse_mode='html', caption=item.get_blocks()[0])
    for block in range(1, len(item.get_blocks())):
        if item.get_blocks()[block]:
            bot.send_message(message.chat.id, item.get_blocks()[block], parse_mode='html') 


if __name__ == "__main__":
    bot.polling(non_stop=True)
