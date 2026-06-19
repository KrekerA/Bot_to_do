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