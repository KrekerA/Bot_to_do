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


@bot.message_handler(commands=['tasks'])
def list_tasks(message):
  users = read_tasks()  # Пытаемся прочитать задачи из файла
  user_id = str(message.chat.id)
  if user_id not in users or not users[user_id]['active']:
    bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
  else:
    if users[user_id]['tasks'] == []:
      bot.send_message(message.chat.id, "Список задач пуст.")
    else:
       user_tasks = users[user_id]['tasks']
       lines = []
       for i, task in enumerate(user_tasks):
         lines.append(f"{i + 1}. {task['text']}")
       bot.send_message(message.chat.id, "\n".join(lines))




bot.polling()