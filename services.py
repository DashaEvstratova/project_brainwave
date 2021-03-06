from os import environ
from contextlib import contextmanager
from time import time
import sqlite3
import datetime
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def get_greeting_text():
    """
    Получение приветственного текста
    :return: str
    """
    return "👋 Привет, я  - твой ассистент! Расскажи мне свое расписание и задания, " \
           "а я помогу тебе с правильным распределением времени"


def get_input_error_text():
    """
    Получение текста о неправильно введённых данных
    :return: str
    """
    return "✖ Извините, вы ввели данные в неправильном формате. Пожалуйста, попробуйте ещё раз"


def get_thanks_text():
    """
    Получение благодарственного текста
    :return: str
    """
    return "😊 Спасибо, что использовали нашего бота!"


def get_text_no_tasks_until_deadline():
    """
    Получение текста о том, что нет заданий до дедлайна
    :return: str
    """
    return "✖ Нет заданий до указанного дедлайна!"


def get_text_successfully_adding_task():
    """
    Получение текста о том, что задание добавлено
    :return: str
    """
    return "☑ Задание успешно добавлено!"


def get_text_successfully_deletion_task():
    """
    Получение текста о том, что задание удалено
    :return: str
    """
    return "☑ Задание успешно удалено!"


def get_text_successfully_adding_event():
    """
    Получение текста о том, что событие добавлено
    :return: str
    """
    return "☑ Событие успешно добавлено!"


def get_text_successfully_deletion_event():
    """
    Получение текста о том, что событие удалено
    :return: str
    """
    return "☑ Событие успешно удалено!"


def get_text_successfully_deletion_events():
    """
    Получение текста о том, что события удалены
    :return: str
    """
    return "☑ События успешно удалены!"


def get_text_no_tasks():
    """
    Получение текста о том, что у пользователя нет заданий
    :return: str
    """
    return "✖ У вас нет заданий!"


def get_text_no_events_on_this_day():
    """
    Получение текста о том, что у пользователя нет событий в выбранный день
    :return: str
    """
    return "✖ У вас нет событий в выбранный день!"


def get_text_limit_exceeded():
    """
    Получение текста о том, что нельзя запрашивать расписание более, чем на неделю вперед
    :return: str
    """
    return "✖ Извините, вы можете смотреть расписание не более, чем на неделю вперёд"


def request_enter_deadline_date_for_tasks():
    """
    Получение текста с просьбой ввести дату, до которой нужно вывести задания
    :return: str
    """
    return "Введите дату, до какого дня вывести задания.\n" \
           "ДД.ММ.ГГГГ\n\n" \
           f"Например, 💬 {datetime.date.today().strftime('%d.%m.%Y')}"


def request_enter_task_and_deadline():
    """
    Получение текста с просьбой ввести задание и его дедлайн
    :return: str
    """
    return "Введите задание и его дедлайн.\n" \
           "Задание ДД.ММ.ГГГГ\n\n" \
           f"Например, 💬 Сделать ДЗ по матану {datetime.date.today().strftime('%d.%m.%Y')}"


def request_enter_number_task():
    """
    Получение текста с просьбой ввести номер удаляемого задания
    :return: str
    """
    return "Введите номер удаляемого задания\n\n" \
           "Например, 💬 1"


def request_enter_number_event():
    """
    Получение текста с просьбой ввести номер удаляемого события
    :return: str
    """
    return "Введите номер удаляемого события\n\n" \
           "Например, 💬 1"


def request_enter_date_to_view_schedule():
    """
    Получения текста с просьбой ввести дату, на которую нужно вывести расписание
    :return: str
    """
    return "Введите дату, на какой день хотите посмотреть расписание.\n" \
           "ДД.ММ.ГГГГ\n\n" \
           f"Например, 💬 {datetime.date.today().strftime('%d.%m.%Y')}"


def request_enter_event_and_date_to_add():
    """
    Получение текста с просьбой ввести дату, на которую нужно добавить событие
    :return: str
    """
    return "Введите событие, дату, на какой день хотите его добавить " \
           "и время начала и окончания события.\n" \
           "ДД.ММ.ГГГГ чч:мм чч:мм\n\n" \
           f"Например, 💬 Матан (практика) {datetime.date.today().strftime('%d.%m.%Y')} 08:30 10:00"


def request_enter_date_to_delete_event():
    """
    Получение текста с просьбой ввести дату, с которой нужно удалить событие
    :return: str
    """
    return "Введите дату, на какой день хотите удалить событие.\n" \
           "ДД.ММ.ГГГГ\n\n" \
           f"Например, 💬 {datetime.date.today().strftime('%d.%m.%Y')}"


def request_enter_type_and_period():
    """
    Получение текста с просьбой ввести тип события и его период
    :return: str
    """
    return "Введите тип события (единоразовое/повторяющееся) " \
           "и период (в днях), если оно повторяющееся\n" \
           "первая буква типа события ДД\n\n" \
           "Например, 💬 п 7"


def request_enter_deletion_type():
    """
    Получение текста с просьбой указать, удалить событие только на этот день или полностью
    :return: str
    """
    return "Введите, как нужно удалить событие: единоразово или полностью\n" \
           "первая буква типа удаления\n\n" \
           "Например, 💬 е"


def user_registration(message):
    """
    Регистрация пользователя: добавление в таблицу users пользователя
    (если не был добавлен ранее), приветственное сообщение
    :param message: Message - вся информация о полученном сообщении
    :return: None
    """
    create_users_table("project.db")

    with working_with_db("project.db") as cursor:
        user_id = message.chat.id
        cursor.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
        data = cursor.fetchone()
        if data is None:
            user_id = (user_id,)
            cursor.execute("INSERT INTO users VALUES(?);", user_id)
            bot.send_message(message.chat.id, get_greeting_text())
        else:
            bot.send_message(message.chat.id, "Вы уже зарегистрированы!")


def date_to_datetime(date):
    """
    Функция, преобразовывающая дату, введённую пользователем в объект datetime.datetime
    :param date: str - дата, введённая пользователем
    :return: datetime.datetime - дата в виде экземпляра класса
    """
    try:
        return datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')
    except ValueError:
        return datetime.datetime.strptime(date, '%d.%m.%Y')


def date_to_timestamp(date):
    """
    Функция, преобразовывающая дату в секунды от 01.01.1970
    :param date: datetime.datetime - дата в виде экземпляра класса
    :return: float - время в секундах
    """
    return date.timestamp()


def date_view(date_timestamp, view):
    """
    Функция, возвращающая дату, конвертированную в формат ДД.ММ.ГГГГ
    :param date_timestamp: float - дата в виде количества секунд от 01.01.1970
    :param view: str - вид отображения (date, time или datetime)
    :return: str - дата в формате ДД.ММ.ГГГГ
    """
    if view == "date":
        return datetime.datetime.fromtimestamp(date_timestamp).strftime("%d.%m.%Y")
    if view == "time":
        return datetime.datetime.fromtimestamp(date_timestamp).strftime("%H:%M")
    if view == "datetime":
        return datetime.datetime.fromtimestamp(date_timestamp).strftime("%d.%m.%Y %H:%M")


def date_validation(date):
    """
    Валидация даты, введённой пользователем
    :param date: str - дата, введённая пользователем
    :return: bool - валидна дата или нет
    """
    try:
        date_to_datetime(date)
    except ValueError:
        return False
    return True


def number_validation(number):
    """
    Валидация номера, введёного пользователем
    :param number: str - номер, введённый пользователем
    :return: bool - валиден номер или нет
    """
    try:
        number = int(number)
    except ValueError:
        return False
    if number < 1:
        return False
    return True


def event_and_deletion_type_validation(event_type):
    """
    Валидация типа события, который ввёл пользователь
    :param event_type: str - тип события, введённый пользователем
    :return: bool - валиден тип или нет
    """
    if event_type in ('п', 'е'):
        return True
    return False


def create_counter():
    """
    Функция, при вызове которой создаётся независимый счётчик
    :return: function
    """
    i = 0

    def inc():
        """
        Функция, которая увеличивает значение i на единицу
        :return: int
        """
        nonlocal i
        i += 1
        return i

    return inc


def schedule_date_limitation(date):
    """
    Проверка, входит ли введённая пользователем дата расписания
    в одну неделю, считая от сегодняшнего дня
    :param date: str - дата, введённая пользователем
    :return: bool - входит или не входит
    """
    today = date_to_datetime(date_view(datetime.datetime.today().timestamp(), 'date'))
    end = today + datetime.timedelta(days=7)
    if today <= date_to_datetime(date) < end:
        return True
    return False


def create_tasks_table(db):
    """
    Создание таблицы tasks в БД
    :return: None
    """
    with working_with_db("project.db") as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                deadline TIMESTAMP,
                user_id INTEGER
            )""")


def create_events_table(db):
    """
    Создание таблицы events в БД
    :return: None
    """
    with working_with_db("project.db") as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                period TIMESTAMP, 
                user_id INTEGER
            )""")


def display_del_add_view_task():
    """
    Функция, которая выводит кнопки взаимодействия с заданиями
    :return: telebot.types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True, one_time_keyboard=True)
    removal = types.KeyboardButton(text="Удалить задание")
    adding = types.KeyboardButton(text="Добавить задание")
    view = types.KeyboardButton(text="Посмотреть задания")
    keyboard.add(removal, adding, view)
    return keyboard


def display_del_add_view_event():
    """
    Функция, которая выводит кнопки взаимодействия с событиями
    :return: telebot.types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True, one_time_keyboard=True)
    removal = types.KeyboardButton(text='Удалить событие из расписания')
    adding = types.KeyboardButton(text='Добавить событие в расписание')
    view = types.KeyboardButton(text='Посмотреть расписание')
    keyboard.add(removal, adding, view)
    return keyboard


def display_schedule_tasks_buttons():
    """
    Функция, которая выводит кнопки "Задания" и "Расписание"
    :return: telebot.types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True, one_time_keyboard=True)
    timetable = types.KeyboardButton(text='Расписание')
    task = types.KeyboardButton(text='Задания')
    keyboard.add(timetable, task)
    return keyboard


def create_users_table(db):
    """
    Создание таблицы users в БД
    :return: None
    """
    with working_with_db(db) as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY 
                )""")


@contextmanager
def working_with_db(db):
    """
    Контекстный менеджер для работы с базой данных
    :param db: str - название базы данных
    :return: sqlite3.Cursor - курсор для работы с базой данных
    """
    connect = sqlite3.connect(db)
    cursor = connect.cursor()
    yield cursor
    connect.commit()
    connect.close()


def delete_obsolete_tasks():
    """
    Функция, удаляющая задания, срок которых истёк
    :return: None
    """
    now = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time())
    now = date_to_timestamp(now)
    with working_with_db("project.db") as cursor:
        cursor.execute(f"DELETE FROM tasks WHERE deadline < {now}")
