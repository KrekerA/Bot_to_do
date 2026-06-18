import telebot
from func import read_tasks
import os
from dotenv import load_dotenv
import sqlite3

# Подключение к бд
DATABASE = 'baza.db'
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)# Создаем экземпляр бота с помощью токена


users = read_tasks()  # Читаем задачи из бд


@bot.message_handler(commands=['start'])# Декоратор для обработки команды /start
def start(message):
    users = read_tasks()
    telegram_id = str(message.chat.id)
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()

    # Проверяет есть ли пользователь в бд, если нет - создает, если есть - активирует
    user = check_users(message, users)
    if user is None:
      cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
      bot.send_message(message.chat.id, 'Привет, я твой помощник для управления задачами! Чтобы узнать мои команды, напиши /help.')
    else:
      cursor.execute("UPDATE users SET active = 1 WHERE telegram_id = ?", (telegram_id,))
      bot.send_message(message.chat.id, 'Привет, я твой бот😊')

    conn.commit()
    conn.close()




@bot.message_handler(commands=['add'])
def add_task(message): # Добавляет задачи пользователя
  users = read_tasks()
  telegram_id = check_users(message, users)
  conn = sqlite3.connect('baza.db')
  cursor = conn.cursor()

  # Проверяет есть ли пользователь и активен ли он
  if telegram_id is None or cursor.execute("SELECT active FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()[0] == 0:
    return bot.send_message(message.chat.id, 'Чтобы начать нажмите /start')
  else:

    # Проверяет текст задачи после команды add
    task = message.text.split(maxsplit=1)
    if len(task) < 2:
      return bot.send_message(message.chat.id, "Пожалуйста, введите текст задачи после команды /add.")
    else:
      task = task[1]
    
      # Добавляет задачу в базу данных
      cursor.execute("INSERT INTO tasks (user_id, text) VALUES ((SELECT id FROM users WHERE telegram_id = ?), ?)", (telegram_id, task))
      bot.send_message(message.chat.id, "Задача добавлена!")
      conn.commit()
      conn.close()


@bot.message_handler(commands=['tasks'])
def list_tasks(message): # Показывает список задач пользователя
  users = read_tasks()
  telegram_id = check_users(message, users)
  conn = sqlite3.connect('baza.db')
  cursor = conn.cursor()

  # Проверяет есть ли пользователь и активен ли он
  if telegram_id is None or cursor.execute("SELECT active FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()[0] == 0:
    return bot.send_message(message.chat.id, 'Чтобы начать нажмите /start')
  else:
    # Запрашивает текст, дату создания задачи и выполнена ли она из бд
    cursor.execute("SELECT text, done, created_at FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)", (telegram_id,))
    tasks = cursor.fetchall()
    conn.close()

    # Если нет задач просит добавить задачи командой add
  if not tasks:
    return bot.send_message(message.chat.id, "Список задач пуст. Чтобы добавить задачу используй /add.")
  else:
    # Показывает задачи пользователю
    lines = []
    for i, (text, done, created_at) in enumerate(tasks):
      lines.append(f"{i + 1}. {text} {'✅' if done else '❌'} (создано: {created_at})")
    return bot.send_message(message.chat.id, "\n".join(lines))




@bot.message_handler(commands=['delete'])
def delete_tasks(message): # Удаляет задачи пользователя
      users = read_tasks()
      telegram_id = check_users(message, users)
      conn = sqlite3.connect('baza.db')
      cursor = conn.cursor()
      
      # Проверяет есть ли пользователь и активен ли он
      if telegram_id is None or cursor.execute("SELECT active FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()[0] == 0: 
        return bot.send_message(message.chat.id, 'Чтобы начать нажмите /start')
      else:
        
        # Проверяет текст задачи после команды delete
        task = message.text.split(maxsplit=1)
        if len(task) < 2:
          return bot.send_message(message.chat.id, "Пожалуйста, введите текст задачи после команды /delete.")
        else:
          task = task[1]

          # Запрашивает задачи пользователя, если их нет - просит добавить
          cursor.execute("SELECT * FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)", (telegram_id,))
          if not cursor.fetchall():
            return bot.send_message(message.chat.id, "Список задач пуст. Чтобы добавить задачу используй /add.")
          else:

            # Если это номер задачи пытается ее удалить
            if task.isdigit():
                cursor.execute("DELETE FROM tasks WHERE id = (SELECT id FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) LIMIT 1 OFFSET ?)", (telegram_id, int(task) - 1))
                if cursor.rowcount == 0: # Если ничего не удаляется сообщает что номер неверный
                  return bot.send_message(message.chat.id, "Неверный номер задачи.")
                else:
                  bot.send_message(message.chat.id, "Задача удалена!")
                  conn.commit()
                  conn.close()

            # Если это текст пытается удалить задачу
            else:
              cursor.execute("DELETE FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) AND text = ?", (telegram_id, task))
              if cursor.rowcount == 0:# Если ничего не удаляется сообщает что задача не найдена
                bot.send_message(message.chat.id, "Задача не найдена в списке.")
              else: 
                bot.send_message(message.chat.id, "Задача удалена!")
                conn.commit()
                conn.close()



@bot.message_handler(commands=['clear'])
def clear_tasks(message): # Удаляет все задачи пользователя
    users =read_tasks()
    telegram_id = check_users(message, users)
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()

    # Проверяет есть ли пользователь и активен ли он
    if telegram_id is None or cursor.execute("SELECT active FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()[0] == 0: 
        return bot.send_message(message.chat.id, 'Чтобы начать нажмите /start')
    else:

      # Пытается удалить задачу
      cursor.execute("DELETE FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)", (telegram_id,))
      if cursor.rowcount == 0: # Если ничего не удаляется сообщает что список пуст
          return bot.send_message(message.chat.id, "Список уже пуст. Чтобы добавить задачу используй /add.")
      else:    
          bot.send_message(message.chat.id, "Все задачи удалены!")
          conn.commit()
          conn.close()



@bot.message_handler(commands=['done'])
def done_tasks(message): # Делает задачу выполненной
  users = read_tasks()
  telegram_id = check_users(message, users)
  conn = sqlite3.connect('baza.db')
  cursor = conn.cursor()

  # Проверяет есть ли пользователь и активен ли он
  if telegram_id is None or cursor.execute("SELECT active FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()[0] == 0: 
        return bot.send_message(message.chat.id, 'Чтобы начать нажмите /start')
  else:

    # Проверяет текст задачи после команды done
    task = message.text.split(maxsplit=1)
    if len(task) < 2:
      return bot.send_message(message.chat.id, "Пожалуйста, введите текст задачи после команды /done.")
    else:
      task = task[1]

      # Запрашивает задачи пользователя, если их нет - просит добавить
      cursor.execute("SELECT * FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)", (telegram_id,))
      if not cursor.fetchall():
        return bot.send_message(message.chat.id, "Список задач пуст. Чтобы добавить задачу используй /add.")
      else:

        # Если это номер задачи пытается отметить ее как выполненная
        if task.isdigit():
            cursor.execute("UPDATE tasks SET done = 1 WHERE id = (SELECT id FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) LIMIT 1 OFFSET ?)", (telegram_id, int(task) - 1))
            if cursor.rowcount == 0: # Если ничего не отмечается сообщает что номер неверный
              return bot.send_message(message.chat.id, "Неверный номер задачи.")
            else:
              bot.send_message(message.chat.id, "Задача отмечена как выполненная!")
              conn.commit()
              conn.close()
        else:
            
            # Если это текст задачи пытается отметить ее как выполненная
            cursor.execute("UPDATE tasks SET done = 1 WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) AND text = ?", (telegram_id, task))
            if cursor.rowcount == 0: # Если ничего не отмечается сообщает что задача не найдена
              return bot.send_message(message.chat.id, "Задача не найдена в списке.")
            else:
                bot.send_message(message.chat.id, "Задача отмечена как выполненная!")
                conn.commit()
                conn.close()
            
     



@bot.message_handler(commands=['undone'])
def undone_tasks(message): # Делает задачу не выполненной
  users = read_tasks()
  telegram_id = check_users(message, users)
  conn = sqlite3.connect('baza.db')
  cursor = conn.cursor()

  # Проверяет есть ли пользователь и активен ли он
  if telegram_id is None or cursor.execute("SELECT active FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()[0] == 0: 
        return bot.send_message(message.chat.id, 'Чтобы начать нажмите /start')
  else:

    # Проверяет текст задачи после команды undone
    task = message.text.split(maxsplit=1)
    if len(task) < 2:
      return bot.send_message(message.chat.id, "Пожалуйста, введите текст задачи после команды /undone.")
    else:
      task = task[1]

    # Запрашивает задачи пользователя, если их нет - просит добавить
      cursor.execute("SELECT * FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)", (telegram_id,))
      if not cursor.fetchall():
        return bot.send_message(message.chat.id, "Список задач пуст. Чтобы добавить задачу используй /add.")
      else:

        # Если это номер задачи пытается отметить ее как  не выполненная
        if task.isdigit():
            cursor.execute("UPDATE tasks SET done = 0 WHERE id = (SELECT id FROM tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) LIMIT 1 OFFSET ?)", (telegram_id, int(task) - 1))
            if cursor.rowcount == 0: # Если ничего не отмечается сообщает что номер неверный
                return bot.send_message(message.chat.id, "Неверный номер задачи.")
            else:
                conn.commit()
                conn.close()
                bot.send_message(message.chat.id, "Задача отмечена как не выполненная!")
        else:
            
            # Если это текст задачи пытается отметить ее как не выполненная
            cursor.execute("UPDATE tasks SET done = 0 WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) AND text = ?", (telegram_id, task))
            if cursor.rowcount == 0: # Если ничего не отмечается сообщает что задача не найдена
                return bot.send_message(message.chat.id, "Задача не найдена в списке.")
            else:
                bot.send_message(message.chat.id, "Задача отмечена как не выполненная!")
                conn.commit()
                conn.close()




@bot.message_handler(commands=['stop'])
def stop(message): # Останавливает бота для пользователя
    users = read_tasks()
    telegram_id = str(message.chat.id)
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()

    # Проверяет есть ли пользователь в бд
    if telegram_id is None:
      return bot.send_message(message.chat.id, 'Чтобы начать нажмите start')
    
    # Проверяет активен ли он
    if cursor.execute("SELECT active FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()[0] == 0:
       return bot.send_message(message.chat.id, 'Бот уже выключен, чтобы начать нажмите /start')
    else:
       
       # Деактивирует пользователя
       cursor.execute("UPDATE users SET active = 0 WHERE telegram_id = ?", (telegram_id,))
       bot.send_message(message.chat.id, 'Бот выключен!')
       conn.commit()
       conn.close()


def check_users(message, users=None): # Проверяет есть ли позьзователь в бд
  if users is None:
    users = read_tasks()
  telegram_id = str(message.chat.id)
  cursor = sqlite3.connect('baza.db').cursor()

  # Запрашивает информацию из таблицы users для конкретного пользователя
  cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
  if not cursor.fetchone():
    return None
  return telegram_id

@bot.message_handler(commands=['help'])
def help(message): # Выводит список команд для бота
   bot.send_message(message.chat.id, 'Команды бота \n' \
   '- /start — зарегистрировать пользователя и активировать бота \n' \
   '- /add <текст задачи> — добавить новую задачу \n' \
   '- /tasks — показать текущий список задач \n' \
   '- /delete <номер или текст задачи> — удалить задачу \n' \
   '- /done <номер или текст задачи> — отметить задачу выполненной \n' \
   '- /undone <номер или текст задачи> — отметить задачу невыполненной \n' \
   '- /clear — удалить все задачи \n' \
   '- /stop — деактивировать бота для текущего пользователя \n' \
   '- /help - доступные команды')



bot.polling()