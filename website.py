import time
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from func import create_database, get_connection
from streamlit_cookies_controller import CookieController
from datetime import datetime

def show_user_tasks(telegram_id): # функция показывающая задачи пользователю
   with get_connection() as conn:
        cursor = conn.cursor()
        # Проверяет есть ли задачи у пользователя
        cursor.execute("""
            SELECT id, text, done, created_at FROM tasks 
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) 
            ORDER BY created_at DESC
        """, (telegram_id,))

        tasks_data = cursor.fetchall()

        if not tasks_data:
            st.info("📭 У вас пока нет задач. Добавьте их через команду /add в Telegram боте")
            st.stop()
            

        # Преобразует полученные задачи в Data Frame с помощью Pandas 
        df = pd.DataFrame(tasks_data, columns=['id', 'text', 'done', 'created_at'])
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


        # Форма для добавления задачи
        with st.form(key="add_task_form", clear_on_submit=True):
            # Текстовое поле для ввода
            task_text = st.text_input("Что нужно сделать?")
            
            # Кнопка отправки формы
            submit_button = st.form_submit_button(label="Добавить задачу")

        if submit_button:
            if task_text.strip() != "":
                
                with get_connection() as conn:
                  cursor = conn.cursor()
                  
                  cursor.execute("INSERT INTO tasks (user_id, text) VALUES ((SELECT id FROM users WHERE telegram_id = ?), ?)", (telegram_id, task_text))
                  conn.commit()
                
                st.success("Задача успешно добавлена!")
                
                # Перезапускает интерфейс, чтобы новая задача сразу появилась в списке ниже
                st.rerun()
            else:
                st.warning("Название задачи не может быть пустым.")


        st.subheader("📋 Ваш список задач")

       # Шапка таблицы
        header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([0.5, 4.7, 4, 6, 3.8])
        with header_col1:
            st.markdown('**№**')
        with header_col2:
            st.markdown('**Название**')
        with header_col3:
            st.markdown('**Статус**')
        with header_col4:
            st.markdown('**Действия**')
        with header_col5:
            st.markdown('**Дата**')
            

        # Улучшеный вывод таблицы задач
        for index, task in enumerate(tasks_data[:5]): # За счет среза выводятся 5 задач
            task_id, text, done, data = task
            number_task = index + 1 # номер задачи
            col1, col2, col3, col4, col5 = st.columns([5, 2, 3, 3, 4])
            
            with col1:
                text = f'{number_task}.     {text}'
                # Если задача выполнена, зачеркивает текст
                st.write(f"~~{text}~~" if done else text)
                
                # Статус задачи
            with col2:
                st.write('✅' if done else '❌')

            with col3:
                # Кнопки выполнить отменить выполнение
                if not done:
                    # Уникальный ключ по id задачи
                    if st.button("Выполнить", key=f"comp_{task_id}"):
                        with get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?;", (task_id,))
                            conn.commit()
                        st.rerun() # Перезапускает интерфейс
                else:
                    if st.button("Отменить выполнение", key=f"uncomp_{task_id}"):
                        with get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tasks SET done = 0 WHERE id = ?;", (task_id,))
                            conn.commit()
                        st.rerun() # Перезапускает интерфейс

            with col4:
                # Кнопка удалить
                if st.button("Удалить", key=f"del_{task_id}"):
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
                        conn.commit()
                    st.rerun() # Перезапускает интерфейс
            
            # Дата создания
            with col5:
                date = data
                db_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                st.write(db_date.strftime("%d.%b.%Y в %H:%M"))


        if len(tasks_data) > 5: # если задач больше 5, скрывает их
            st.write("")
            # Раскрывающийся блок
            with st.expander(f"Показать все({len(tasks_data)-5})"):

                # Выводит оставшиеся задачи с помощью среза и начинает отсчет с 5
                for index, task in enumerate(tasks_data[5:], start = 5):
                    task_id, text, done, data = task
                    number_task = index + 1 # номер задачи
                    col1, col2, col3, col4, col5 = st.columns([5, 2, 3, 3, 4])
            
                    with col1:
                        text = f'{number_task}.     {text}'
                        # Если задача выполнена, зачеркивает текст
                        st.write(f"~~{text}~~" if done else text)
                        
                        # показывает статус задачи
                    with col2:
                        st.write('✅' if done else '❌')

                    with col3:
                        if not done:
                            # Уникальный ключ по id задачи
                            if st.button("Выполнить", key=f"comp_{task_id}"):
                                with get_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?;", (task_id,))
                                    conn.commit()
                                st.rerun() # Перезапускает интерфейс
                        else:
                            if st.button("Отменить выполнение", key=f"uncomp_{task_id}"):
                                with get_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE tasks SET done = 0 WHERE id = ?;", (task_id,))
                                    conn.commit()
                                st.rerun() # Перезапускает интерфейс

                    with col4:
                        if st.button("Удалить", key=f"del_{task_id}"):
                            with get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
                                conn.commit()
                            st.rerun() # Перезапускает интерфейс
                    
                    # дата создания
                    with col5:
                        date = data
                        db_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        st.write(db_date.strftime("%d.%b.%Y в %H:%M"))
            


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

DATABASE = 'baza.db'

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
        else:
            user_id, is_active = user_result

            if not is_active:
                st.warning("⚠️ Ваш аккаунт деактивирован")
                st.stop()

            st.success("✅ ID верифицирован")
            show_user_tasks(telegram_id)
            
        
        
            if remember_me:
                try:
                    controller.set("logged_in_user", telegram_id, max_age=60*60*24*30)

                except Exception:
                    st.warning("Не удалось сохранить cookie. Попробуйте разрешить куки в браузере.")
            time.sleep(0.5)        
            st.rerun()


else:
    show_user_tasks(st.session_state["telegram_id"])
    if st.button("Забыть меня"):
        controller.remove("logged_in_user") # Удаляет cookie
        del st.session_state["telegram_id"]    # Удаляет из сессии
        time.sleep(0.5)
        st.rerun()                          # Перезапускает страницу