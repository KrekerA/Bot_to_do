import sqlite3
import streamlit as st
from func import create_database, get_connection

# Заголовок сайта
st.set_page_config(page_title="Трекер Продуктивности", layout="wide")
st.title("📊 Дашборд аналитики твоего обучения")
st.subheader("Данные загружаются из твоего Telegram-бота")


#  Подключает к бд и создает если её нет
try:
    get_connection()
except:
    create_database()
    get_connection()



# Просит ввести ID пользователя
telegram_id = st.text_input("Введите ваш Telegram ID для просмотра аналитики: ")

if not telegram_id:
    st.info("Введите Telegram ID чтобы просмотреть аналитику")
    st.stop()

with get_connection() as conn:
  # Проверяет есть ли пользователь и активен ли он
  cursor = conn.cursor()
  cursor.execute("SELECT id, active FROM users WHERE telegram_id = ?", (telegram_id,))
  user_result = cursor.fetchone()

  if not user_result:
    st.warning("❌ Пользователь не найден. Пожалуйста, запустите /start в Telegram боте")
    st.stop()

  user_id, is_active = user_result

  if not is_active:
    st.warning("⚠️ Ваш аккаунт деактивирован")
    st.stop()

  st.success("✅ ID верифицирован")


  # Проверяет есть ли задачи у пользователя
  cursor.execute("""
    SELECT text, done, created_at FROM tasks 
    WHERE user_id = ? 
    ORDER BY created_at DESC
  """, (user_id,))

  tasks_data = cursor.fetchall()

  if not tasks_data:
    st.info("📭 У вас пока нет задач. Добавьте их через команду /add в Telegram боте")
    st.stop()