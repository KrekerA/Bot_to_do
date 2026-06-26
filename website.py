import time
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from func import create_database, get_connection
from streamlit_cookies_controller import CookieController

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


# Для работы с cookie files
controller = CookieController()

# Пытается достать имя пользователя из cookie files браузера
saved_user = controller.get("logged_in_user")

# Если в cookie files есть пользователь, записывает его в session_state Streamlit
if saved_user and "telegram_id" not in st.session_state:
    st.session_state["telegram_id"] = saved_user

if "telegram_id" not in st.session_state:
    # Просит ввести ID пользователя
    telegram_id = st.text_input("Введите ваш Telegram ID для просмотра аналитики: ")
    remember_me = st.checkbox("Запомнить меня", key="remember_me")

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


    # Преобразует полученные задачи в Data Frame с помощью Pandas 
    df = pd.DataFrame(tasks_data, columns=['text', 'done', 'created_at'])
    df['done'] = df['done'].astype(bool)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date


    # Выводит сколько всего задач и сколько из них выполнено и невыполнено
    total_tasks = len(df)
    completed_tasks = df['done'].sum()
    pending_tasks = total_tasks - completed_tasks

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Всего задач", value=total_tasks)
    with col2:
        st.metric(label="Выполнено ✅", value=completed_tasks)
    with col3:
        st.metric(label="В процессе ⏳", value=pending_tasks)



    st.markdown("---")

    # Создает график выполненых задач с помощью plotly
    st.subheader("📈 Динамика выполненных задач")
    daily_completed = df[df['done']].groupby('date').size().reset_index(name='count')

    if not daily_completed.empty:
        fig = px.bar(daily_completed, x="date", y="count", 
                    labels={"date": "Дата", "count": "Выполненные задачи"},
                    title="Количество выполненных задач по дням",
                    color="count", color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)


    # 5. Выводит таблицу задач
    st.subheader("📋 Ваш список задач")
    display_df = df[['text', 'done', 'created_at']].copy()
    display_df['Статус'] = display_df['done'].apply(lambda x: '✅ Выполнено' if x else '⏳ В процессе')
    display_df = display_df[['text', 'Статус', 'created_at']].rename(
        columns={'text': 'Задача', 'created_at': 'Дата создания'})
    st.dataframe(display_df, use_container_width=True, hide_index=True) 
    
    if remember_me:
        try:
            controller.set("logged_in_user", telegram_id, max_age=60*60*24*30)

        except Exception:
            st.warning("Не удалось сохранить cookie. Попробуйте разрешить куки в браузере.")
    time.sleep(0.5)        
    st.rerun()


else:
    with get_connection() as conn:
        cursor = conn.cursor()
        telegram_id = st.session_state["telegram_id"]
        cursor.execute("""
            SELECT text, done, created_at FROM tasks 
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) 
            ORDER BY created_at DESC
        """, (telegram_id,))
        tasks_data = cursor.fetchall()
        if not tasks_data:
            st.info("📭 У вас пока нет задач. Добавьте их через команду /add в Telegram боте")
            st.stop()
            

        # Преобразуем в DataFrame
        df = pd.DataFrame(tasks_data, columns=['text', 'done', 'created_at'])
        df['done'] = df['done'].astype(bool)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date'] = df['created_at'].dt.date

        # 3. Блок главных метрик
        total_tasks = len(df)
        completed_tasks = df['done'].sum()
        pending_tasks = total_tasks - completed_tasks

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Всего задач", value=total_tasks)
        with col2:
            st.metric(label="Выполнено ✅", value=completed_tasks)
        with col3:
            st.metric(label="В процессе ⏳", value=pending_tasks)

        st.markdown("---")

        # 4. График выполненных задач по дням
        st.subheader("📈 Динамика выполненных задач")
        daily_completed = df[df['done']].groupby('date').size().reset_index(name='count')

        if not daily_completed.empty:
            fig = px.bar(daily_completed, x="date", y="count", 
                        labels={"date": "Дата", "count": "Выполненные задачи"},
                        title="Количество выполненных задач по дням",
                        color="count", color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)

        # 5. Вывод таблицы задач
        st.subheader("📋 Ваш список задач")
        display_df = df[['text', 'done', 'created_at']].copy()
        display_df['Статус'] = display_df['done'].apply(lambda x: '✅ Выполнено' if x else '⏳ В процессе')
        display_df = display_df[['text', 'Статус', 'created_at']].rename(
            columns={'text': 'Задача', 'created_at': 'Дата создания'}
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)