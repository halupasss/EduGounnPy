import json
import logging
from operator import le
import requests


DEVKEY = 'd9ca53f1e47e9d2b9493d35e2a5e36'


class School:
    number: str # код школы
    title : str # название школы
    vendor: str # вендор школы

    def __init__(self, number: str, title: str, vendor: str):
        self.number = number
        self.title = title
        self.vendor = vendor

    def __str__(self):
        return self.title


class File:
    name: str | None
    link: str | None

    def __init__(self, name: str, link: str):
        self.name = name
        self.link = link

    def __str__(self):
        return self.name


class Mark:
    value   : str | None
    comment : str | None

    def __init__(
        self, value: str, comment: str
    ): 
        self.value = value
        self.comment = comment

    def __str__(self):
        return self.value


class Lesson:
    name    : str # Название предмета
    index   : str # позиция предмета
    room    : str # Кабинет
    teacher : str # ФИО Учителя
    homework: list[str] | None # Дз
    files   : list[File]| None # Прикрепленные файлы
    marks   : list[Mark]| None # Оценки

    def __init__(self):
        self.name = ''
        self.index = ''
        self.room = ''
        self.teacher = ''
        self.homework = []
        self.files = []
        self.marks = []

    def __str__(self):
        return self.name


class Day:
    date    : str # дата в виде числа
    title   : str # название дня
    lessons : list[Lesson]
    today   : bool = False
    vacation: bool = False

    def __init__(self, date: str, title: str, lessons: list[Lesson]):
        self.date = date
        self.title = title
        self.lessons = lessons

    def __str__(self):
        return self.title


class Week:
    def __init__(self, week: dict):
        self.week = week

        self.week_array = [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday, self.saturday]

    @property
    def monday(self) -> Day:
        """ Понедельник 
                * property функции можно вызывать без скобок
            т.е week.monday
        """
        return self.week['Понедельник']

    @property
    def tuesday(self) -> Day:
        """ Вторник
                * property функции можно вызывать без скобок
            т.е tuesday.monday
        """
        return self.week['Вторник']

    @property
    def wednesday(self) -> Day:
        """ Среда
                * property функции можно вызывать без скобок
            т.е wednesday.monday
        """
        return self.week['Среда']
    
    @property
    def thursday(self) -> Day:
        """ Четверг
                * property функции можно вызывать без скобок
            т.е thursday.monday
        """
        return self.week['Четверг']

    @property
    def friday(self) -> Day:
        """ Пятница
                * property функции можно вызывать без скобок
            т.е friday.monday
        """
        return self.week['Пятница']

    @property
    def saturday(self) -> Day:
        """ Суббота
                * property функции можно вызывать без скобок
            т.е saturday.monday
        """
        return self.week['Суббота']

    def __str__(self):
        return (
            str(self.monday)    +
            str(self.tuesday)   +
            str(self.wednesday) +
            str(self.thursday)  +
            str(self.friday)    +
            str(self.saturday)
        )

    def __getitem__(self, key):
        return self.week_array[key]


class User:
    id          : str # id пользователя
    roles       : list # student, teacher, administrator...
    relation    : str # child, parent...
    firstname   : str # имя
    lastname    : str # фамилия
    middlename  : str # очество
    title       : str # ФИО
    gender      : str # пол
    classname   : str # класс
    parallel    : str # параллель
    city        : str # город + район
    email       : str # email
    region      : str # регион
    token       : str # токен пользователя для api
    message_signature: str # подпись в конце сообщения
    school      : School

    def __init__(self, token: str, username: str, password: str, api):
        self.token = token
        self.username = username
        self.password = password

        self.api = api

        data = api.get_user_data(username, password)

        self.id         = data['response']['result']['id']
        self.roles      = data['response']['result']['roles']
        self.relation   = data['response']['result']['relations']['students'][self.id]['rel']
        self.firstname  = data['response']['result']['firstname']
        self.lastname   = data['response']['result']['lastname']
        self.middlename = data['response']['result']['middlename']
        self.gender     = data['response']['result']['gender']
        self.title      = data['response']['result']['title']
        self.classname  = data['response']['result']['relations']['students'][self.id]['class']
        self.parallel   = data['response']['result']['relations']['students'][self.id]['parallel']
        self.city       = data['response']['result']['relations']['students'][self.id]['city']
        self.email      = data['response']['result']['email']
        self.region     = data['response']['result']['region']
        self.message_signature = data['response']['result']['messageSignature']

        self.school = School(
            number=data['response']['result']['relations']['schools'][0]['number'],
            title=data['response']['result']['relations']['schools'][0]['title_full'],
            vendor=data['response']['result']['vendor']
        )

    def get_diary(self) -> Week:
        """ Псевдоним для EduApi.get_user_diary()

            * Не требует аргументов для авторизации
        """

        diary = self.api.get_user_diary(self.username, self.password)

        return diary

    def get_current_day(self) -> Day:
        """ Псевдоним для EduApi.get_current_day()

            * Не требует аргументов для авторизации
        """

        day = self.api.get_current_day(self.username, self.password)

        return day

    def __str__(self):
        return self.title


class EduApi:
    def __init__(self):
        self._auth_tokens = {} # username: auth_token
        self._users = {}       # username: class 'User'
        self._logger = logging.getLogger(__name__)

    def auth(self, username: str, password: str) -> User:
        """ Авторизация пользователя (получение токена для api)

            * Возвращает объект пользователя User

            Аргументы:
                username: str - Логин пользователя
                password: str - Пароль
        """
        auth_url = (
            f'https://edu.gounn.ru/apiv3/auth?devkey={DEVKEY}'
            f'&out_format=json&auth_token&login={username}&password={password}&vendor=edu'
        )

        auth_response = requests.get(auth_url)

        json_response = json.loads(auth_response.text)

        """
        {
            "response": {
                "state":200,
                "error":null,
                "result": {
                    "token": token,
                    "expires": date D.M.Y H.M.S format
                }
            }
        }
        """

        token = json_response['response']['result']['token']
        error = json_response['response']['error']

        if error != None:
            self._logger.info(f'{username}::{error}')

        if not self._auth_tokens.get(username):
            self._auth_tokens[username] = token

        user = User(token, username, password, self)

        if not self._users.get(username):
            self._users[username] = user

        return user

    def get_user(self, username: str, password: str) -> User:
        """ Получение объекта пользователя User из кэша

            * Возвращает объект пользователя User

            Аргументы:
                username: str - Логин пользователя
                password: str - Пароль
        """
        if not self._users.get(username):
            self._users[username] = self.auth(username, password)

        return self._users.get(username)

    def get_user_data(self, username: str, password: str):
        """ Возвращает данные о пользователе из getrules (Для инициализации User)

            Аргументы:  
                username: str - Логин пользователя
                password: str - Пароль
        """

        if not self._auth_tokens.get(username):
            self._auth_tokens[username] = self.auth(username, password).token

        authtoken = self._auth_tokens.get(username)

        data_url = (
            f'https://edu.gounn.ru/apiv3/getrules?devkey={DEVKEY}&'
            f'out_format=json&auth_token={authtoken}&vendor=edu'
        )

        data_response = requests.get(data_url)

        json_formatted = json.loads(data_response.text)

        return json_formatted

    def get_user_diary(self, username: str, password: str) -> Week:
        """ Возвращает данные о текущей неделе (дневник)

            Аргументы:
                username: str - Логин пользователя
                password: str - Пароль 
        """

        week = {}

        if not self._auth_tokens.get(username):
            self._auth_tokens[username] = self.auth(username, password).token

        auth_token = self._auth_tokens.get(username)

        diary_url = (
            f'https://edu.gounn.ru/apiv3/getdiary?devkey={DEVKEY}&'
            f'out_format=json&auth_token={auth_token}&vendor=edu'
        )

        diary_response = requests.get(diary_url)

        diary = json.loads(diary_response.text)

        user = self.get_user(username, password)

        days_path = diary['response']['result']['students'][user.id]['days']

        for day in days_path:
            day_date = day
            day_title = days_path[day]['title']
            day_lessons = []

            is_current_day  = False
            is_vacation_day = False

            if days_path[day].get('alert'):
                if days_path[day]['alert'] == 'today':
                    is_current_day = True

                if days_path[day]['alert'] == 'vacation':
                    is_vacation_day = True


            for lesson in days_path[day]['items']:
                lesson_path     = days_path[day]['items'][lesson]
                lesson_name     = lesson_path['name']
                lesson_index    = lesson_path['num']
                lesson_room     = lesson_path['room']
                lesson_teacher  = lesson_path['teacher']

                lesson_homework = []
                lesson_marks    = []
                lesson_files    = []

                for homework in lesson_path['homework']:
                    lesson_homework.append(lesson_path['homework'][homework]['value'])

                if lesson_path.get('files'):
                    for index in range(len(lesson_path['files'])):
                        lesson_files.append(
                            File(
                                name=lesson_path['files'][index]['filename'],
                                link=lesson_path['files'][index]['link']
                            )
                        )

                if lesson_path.get('assessments'):
                    for index in range(len(lesson_path['assessments'])):
                        lesson_marks.append(
                            Mark(
                                value=lesson_path['assessments'][index]['value'],
                                comment=lesson_path['assessments'][index]['comment']
                            )
                        )

                lesson = Lesson()

                lesson.name     = lesson_name
                lesson.index    = lesson_index
                lesson.room     = lesson_room
                lesson.teacher  = lesson_teacher
                lesson.homework = lesson_homework
                lesson.marks    = lesson_marks
                lesson.files    = lesson_files

                day_lessons.append(lesson)
                
            day = Day(day_date, day_title, day_lessons)

            day.today       = is_current_day
            day.vacation    = is_vacation_day

            if not week.get(day_title):
                week[day_title] = day

        return Week(week)

    def get_current_day(self, username: str, password: str) -> Day:
        """ Возвращает объект текущего дня Day

            Аргументы:
                username: str - Логин пользователя
                password: str - Пароль
        """

        diary = self.get_user_diary(username, password)

        for day in diary:
            if day.today:
                return day
