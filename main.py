import telebot
from bot import TOKEN
from json import save_tasks, read_tasks


bot = telebot.TeleBot(TOKEN)# Создаем экземпляр бота с помощью токена
