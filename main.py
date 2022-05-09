from os import environ
from datetime import timedelta
import sqlite3
import telebot
from telebot import types
from dotenv import load_dotenv
from services import user_registration, date_to_timestamp, date_view, \
    date_validation, number_validation, get_input_error_text, get_thanks_text, \
    request_enter_deadline_date_for_tasks, get_text_no_tasks_until_deadline, \
    get_text_successfully_adding_task, get_text_successfully_deletion_task, \
    request_enter_task_and_deadline, request_enter_number_task, request_enter_date_to_view_schedule, \
    request_enter_event_and_date_to_add, request_enter_date_to_delete_event, create_counter, \
    get_test_no_tasks, request_enter_type_and_period, event_type_validation, \
    get_text_successfully_adding_event

load_dotenv()

TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    user_registration(message)
    startKBoart = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    timetable = types.KeyboardButton(text='Расписание')
    task = types.KeyboardButton(text='Задания')
    startKBoart.add(timetable, task)
    bot.send_message(message.chat.id, 'Что вы хотите сделать?', reply_markup=startKBoart)


@bot.message_handler(func=lambda message: message.text == "Расписание")
def display_schedule_buttons(message):
    startKBoart = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    removal = types.KeyboardButton(text='Удалить событие из рaсписания')
    adding = types.KeyboardButton(text='Добавить событие в расписание')
    view = types.KeyboardButton(text='Посмотреть расписание')
    startKBoart.add(removal, adding, view)
    bot.send_message(message.chat.id, 'Каков будет следующий шаг?)', reply_markup=startKBoart)


@bot.message_handler(regexp="Удалить событие из рaсписания")
def remove_event(message):
    sent = bot.reply_to(message, request_enter_date_to_delete_event())
    bot.register_next_step_handler(sent, remove_event_helper)


def remove_event_helper(message):
    message_to_save = message.text


@bot.message_handler(regexp="Добавить событие в расписание")
def add_event(message):
    sent = bot.reply_to(message, request_enter_event_and_date_to_add())
    bot.register_next_step_handler(sent, first_add_event_helper)


def first_add_event_helper(message):
    message_to_save = message.text
    description, start_date, end_date = message_to_save[:-23], message_to_save[-22:-6], \
                                        message_to_save[-22:-11] + message_to_save[-5:]

    # Валидация введённых данных
    if not date_validation(start_date):
        bot.send_message(message.chat.id, get_input_error_text())
        return
    if not date_validation(end_date):
        bot.send_message(message.chat.id, get_input_error_text())
        return

    sent = bot.reply_to(message, request_enter_type_and_period())
    bot.register_next_step_handler(sent, second_add_event_helper, description, start_date, end_date)


def second_add_event_helper(message, description, start_date, end_date):
    message_to_save = message.text
    event_type = message_to_save[:1]
    if event_type == 'п':
        period = message_to_save[2:]

    # Валидация введённых данных
    if not event_type_validation(event_type):
        bot.send_message(message.chat.id, get_input_error_text())
        return
    if event_type == 'п':
        if not number_validation(period):
            bot.send_message(message.chat.id, get_input_error_text())
            return

    # Соединение с db и создание таблицы events
    connect = sqlite3.connect("project.db")
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            repeat BOOL,
            period TIMESTAMP, 
            user_id INTEGER
        )""")
    connect.commit()

    # Добавление события в db
    event_type = 1 if event_type == 'п' else 0
    if event_type:
        event = description, date_to_timestamp(start_date), date_to_timestamp(end_date), \
                event_type, timedelta(int(period)).total_seconds(), message.chat.id
        cursor.execute("INSERT INTO events VALUES(null, ?, ?, ?, ?, ?, ?);", event)
    else:
        event = description, date_to_timestamp(start_date), date_to_timestamp(end_date), \
                event_type, message.chat.id
        cursor.execute("INSERT INTO events VALUES(null, ?, ?, ?, ?, null, ?);", event)
    connect.commit()
    connect.close()

    bot.send_message(message.chat.id, get_text_successfully_adding_event())


@bot.message_handler(regexp="Посмотреть расписание")
def view_schedule(message):
    sent = bot.reply_to(message, request_enter_date_to_view_schedule())
    bot.register_next_step_handler(sent, view_schedule_helper)


def view_schedule_helper(message):
    message_to_save = message.text


@bot.message_handler(func=lambda message: message.text == "Задания")
def display_tasks_buttons(message):
    startKBoart = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    removal = types.KeyboardButton(text="Удалить задание")
    adding = types.KeyboardButton(text="Добавить задание")
    view = types.KeyboardButton(text="Посмотреть задания")
    startKBoart.add(removal, adding, view)
    bot.send_message(message.chat.id, "Каков будет следующий шаг?)", reply_markup=startKBoart)


@bot.message_handler(regexp="Удалить задание")
def remove_task(message):
    connect = sqlite3.connect("project.db")
    cursor = connect.cursor()
    user_id = message.chat.id
    cursor.execute(f"SELECT * FROM tasks WHERE user_id = {user_id} ORDER BY deadline;")
    tasks = cursor.fetchall()
    counter = create_counter()
    out = ""
    for task in tasks:
        out += f"{counter()}. {task[1]} (до {date_view(task[2])})\n"
    if out == "":
        bot.send_message(message.chat.id, get_test_no_tasks())
    else:
        bot.send_message(message.chat.id, out)
    cursor.close()

    sent = bot.reply_to(message, request_enter_number_task())
    bot.register_next_step_handler(sent, remove_task_helper)


def remove_task_helper(message):
    number = message.text

    # Валидация введённых данных
    if not number_validation(number):
        bot.send_message(message.chat.id, get_input_error_text())
        return

    connect = sqlite3.connect("project.db")
    cursor = connect.cursor()
    user_id = message.chat.id
    cursor.execute(f"SELECT * FROM tasks WHERE user_id = {user_id} ORDER BY deadline;")
    for _ in range(int(number)):
        task = cursor.fetchone()
    cursor.execute(f"DELETE FROM tasks WHERE description = '{task[1]}' AND deadline = {task[2]};")
    connect.commit()
    connect.close()

    bot.send_message(message.chat.id, get_text_successfully_deletion_task())


@bot.message_handler(regexp="Добавить задание")
def add_task(message):
    sent = bot.reply_to(message, request_enter_task_and_deadline())
    bot.register_next_step_handler(sent, add_task_helper)


def add_task_helper(message):
    message_to_save = message.text
    description, deadline = message_to_save[:-11], message_to_save[-10:]

    # Валидация введённых данных
    if not date_validation(deadline):
        bot.send_message(message.chat.id, get_input_error_text())
        return

    # Соединение с db и создание таблицы tasks
    connect = sqlite3.connect("project.db")
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            deadline TIMESTAMP,
            user_id INTEGER
        )""")
    connect.commit()

    # Добавление задания в db
    task = description, date_to_timestamp(deadline), message.chat.id
    cursor.execute("INSERT INTO tasks VALUES(null, ?, ?, ?);", task)
    connect.commit()
    connect.close()

    bot.send_message(message.chat.id, get_text_successfully_adding_task())


@bot.message_handler(regexp="Посмотреть задания")
def view_tasks(message):
    sent = bot.reply_to(message, request_enter_deadline_date_for_tasks())
    bot.register_next_step_handler(sent, view_tasks_helper)


def view_tasks_helper(message):
    message_to_save = message.text
    description, deadline = message_to_save[:-11], message_to_save[-10:]

    # Валидация введённых данных
    if not date_validation(deadline):
        bot.send_message(message.chat.id, get_input_error_text())
        return

    date = date_to_timestamp(deadline)

    connect = sqlite3.connect("project.db")
    cursor = connect.cursor()
    user_id = message.chat.id
    cursor.execute(f"SELECT * FROM tasks WHERE user_id = {user_id} ORDER BY deadline;")
    tasks = cursor.fetchall()
    counter = create_counter()
    out = ""
    for task in tasks:
        if int(date) >= task[2]:
            out += f"{counter()}. {task[1]} (до {date_view(task[2])})\n"
    if out == "":
        bot.send_message(message.chat.id, get_text_no_tasks_until_deadline())
    else:
        bot.send_message(message.chat.id, out)
    cursor.close()


@bot.message_handler(commands=["delete"])
def delete(message):
    # "Удаление" пользователя: удаление всех данных, связанных с id пользователя
    connect = sqlite3.connect("project.db")
    cursor = connect.cursor()
    user_id = message.chat.id
    cursor.execute(f"DELETE FROM users WHERE user_id = {user_id}")
    try:
        cursor.execute(f"DELETE FROM tasks WHERE user_id = {user_id}")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute(f"DELETE FROM events WHERE user_id = {user_id}")
    except sqlite3.OperationalError:
        pass
    connect.commit()
    bot.send_message(message.chat.id, get_thanks_text())
    cursor.close()


print("Bot started working...")
bot.polling()
