import telebot
from bot import TOKEN
from json import save_tasks, read_tasks


bot = telebot.TeleBot(TOKEN)# Создаем экземпляр бота с помощью токена


try:

      tasks = read_tasks()  # Пытаемся прочитать задачи из файла

except FileNotFoundError:
      users = {} # Если файл не найден, создаем пустой словарь для хранения



@bot.message_handler(commands=['add'])
def add_task(message):
  read_tasks()
  user_id = str(message.chat.id)
  if not users[user_id]['active'] or user_id not in users:
    bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
  else:
    task = message.text.replace("/add ", "")# Получаем текст задачи, удаляя команду /add из сообщения
    tasks = {"text": task, "done": False}  # Создаем словарь с задачами для данного пользователя
    users[user_id]['tasks'].append(tasks)
    save_tasks(users)  # Сохраняем задачи в файл

    bot.send_message(message.chat.id, "Задача добавлена!")


bot.polling()