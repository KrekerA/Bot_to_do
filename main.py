import telebot
from func import save_tasks, read_tasks
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")



bot = telebot.TeleBot(TOKEN)# Создаем экземпляр бота с помощью токена


try:

      users = read_tasks()  # Пытаемся прочитать задачи из файла

except FileNotFoundError:
      users = {} # Если файл не найден, создаем пустой словарь для хранения


@bot.message_handler(commands=['start'])# Декоратор для обработки команды /start
def start(message):
    users = read_tasks()
    user_id = str(message.chat.id)
    if user_id not in users:
      users[user_id] = {'active': True, 'tasks': []} # Инициализируем словарь для хранения задач пользователя
    else:
      users[user_id]['active'] = True # Если пользователь уже существует, просто активируем его
    save_tasks(users)
    bot.send_message(message.chat.id, 'Привет, я твой бот😊')




@bot.message_handler(commands=['add'])
def add_task(message):
  users = read_tasks()
  user_id = str(message.chat.id)
  if user_id not in users or not users[user_id]['active']:
    return bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
  else:
    task = message.text.replace("/add ", "").strip() # Получаем текст задачи, удаляя команду /add из сообщения
    if not task or task == "/add":
      return bot.send_message(message.chat.id, "Пожалуйста, введите текст задачи после команды /add.")
    else:
      tasks = {"text": task, "done": False}  # Создаем словарь с задачами для данного пользователя
      users[user_id]['tasks'].append(tasks)
      save_tasks(users)  # Сохраняем задачи в файл

      bot.send_message(message.chat.id, "Задача добавлена!")


@bot.message_handler(commands=['tasks'])
def list_tasks(message):
  users = read_tasks()
  user_id = str(message.chat.id)
  if user_id not in users or not users[user_id]['active']:
    return bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
  else:
    if users[user_id]['tasks'] == []:
      bot.send_message(message.chat.id, "Список задач пуст.")
    else:
       user_tasks = users[user_id]['tasks']
       lines = []
       for i, task in enumerate(user_tasks):
         lines.append(f"{i + 1}. {task['text']} {'✅' if task['done'] else '❌'}")
       bot.send_message(message.chat.id, "\n".join(lines))




@bot.message_handler(commands=['delete'])
def delete_tasks(message):
  task = message.text.replace("/delete ", "")
  users = read_tasks()
  user_id = str(message.chat.id)
  if user_id not in users or not users[user_id]['active']:
    return bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
  else:
    if users[user_id]['tasks'] == []:
      bot.send_message(message.chat.id, "Список задач пуст.")
    else:
      try:
        if task.isdigit():
          try:
            users[user_id]['tasks'].pop(int(task) - 1)
            save_tasks(users)  # Сохраняем задачи в файл
            return bot.send_message(message.chat.id, "Задача удалена!")
          except IndexError:
            return bot.send_message(message.chat.id, "Неверный номер задачи.")
        else:
          for item in users[user_id]['tasks']:
            if item['text'] == task:
              users[user_id]['tasks'].remove(item)
              save_tasks(users)  # Сохраняем задачи в файл
              return bot.send_message(message.chat.id, "Задача удалена!")
          return bot.send_message(message.chat.id, "Задача не найдена в списке.")
            
      except ValueError:
          return bot.send_message(message.chat.id, "Задача не найдена в списке.")      



@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    users =read_tasks()
    user_id = str(message.chat.id)
    if user_id not in users or not users[user_id]['active']:
      bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
    else:
      if users[user_id]['tasks'] == []:
          bot.send_message(message.chat.id, "Список пуст")
      else:    
          users[user_id]['tasks'] = []
          save_tasks(users)
          bot.send_message(message.chat.id, "Все задачи удалены!")



@bot.message_handler(commands=['done'])
def done_tasks(message):
  task = message.text.replace("/done ", "")
  users = read_tasks()
  user_id = str(message.chat.id)
  if user_id not in users or not users[user_id]['active']:
    bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
  else:
    if users[user_id]['tasks'] == []:
      bot.send_message(message.chat.id, "Список задач пуст.")
    else:
      try:
        if task.isdigit():
          try:
            if users[user_id]['tasks'][int(task) - 1]['done']:
              return bot.send_message(message.chat.id, "Задача уже отмечена как выполненная.")
            else:
              users[user_id]['tasks'][int(task) - 1]['done'] = True
              save_tasks(users)
              return bot.send_message(message.chat.id, "Задача отмечена как выполненная!")
          except IndexError:
              return bot.send_message(message.chat.id, "Неверный номер задачи.")
        else:
            for item in users[user_id]['tasks']:
              if item['text'] == task:
                item['done'] = True
                save_tasks(users)
                return bot.send_message(message.chat.id, "Задача отмечена как выполненная!")
            return bot.send_message(message.chat.id, "Задача не найдена в списке.")
      except ValueError:
            return bot.send_message(message.chat.id, "Задача не найдена в списке.")



@bot.message_handler(commands=['undone'])
def undone_tasks(message):
  task = message.text.replace("/undone ", "")
  users = read_tasks()
  user_id = str(message.chat.id)
  if user_id not in users or not users[user_id]['active']:
    bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
  else:
    if users[user_id]['tasks'] == []:
      bot.send_message(message.chat.id, "Список задач пуст.")
    else:
      try:
        if task.isdigit():
            try:
              if not users[user_id]['tasks'][int(task) - 1]['done']:
                return bot.send_message(message.chat.id, "Задача уже отмечена как не выполненная.")
              else:
                users[user_id]['tasks'][int(task) - 1]['done'] = False
                save_tasks(users)  # Сохраняем задачи в файл
                bot.send_message(message.chat.id, "Задача отмечена как не выполненная!")
            except IndexError:
              return bot.send_message(message.chat.id, "Неверный номер задачи.")
        else:
            for item in users[user_id]['tasks']:
              if item['text'] == task:
                item['done'] = False
                save_tasks(users)  # Сохраняем задачи в файл
                return bot.send_message(message.chat.id, "Задача отмечена как не выполненная!")
            return bot.send_message(message.chat.id, "Задача не найдена в списке.")
      except ValueError:
            return bot.send_message(message.chat.id, "Задача не найдена в списке.")




@bot.message_handler(commands=['stop'])
def stop(message):
    users = read_tasks()
    user_id = str(message.chat.id)
    if not users[user_id]['active']:
       bot.send_message(message.chat.id, 'Бот уже выключен')
    else:
       bot.send_message(message.chat.id, 'Бот выключен')
       users[user_id]['active'] = False
       save_tasks(users)

bot.polling()