import logging
import datetime
import requests
from bs4 import BeautifulSoup

import utils
from user_session import UserSession
from user import User, Week, Quarter
from day import Day
from lesson import Lesson, BaseLesson

from enum import Enum

logging.basicConfig(level=logging.INFO)


# enum status code
class eStatusCode(Enum):
    NORMAL = 200
    LOGIN_FAILED = 400
    NOT_FOUND = 404
    FORBIDDEN = 403


quarters = [
        '',
        '/sp.I+четверть',
        '/sp.II+четверть',
        '/sp.III+четверть',
        '/sp.IV+четверть',
]

class EduApi:
    def __init__(self):
        self._logger = logging.getLogger(__file__)
        self._user_sessions = {}

    async def auth(self, username: str, password: str) -> User:
        """ Логинится в аккаунт (обязательно)

            Возвращает User class

            Аргументы:
                username: str -- Логин пользователя
                password: str -- Пароль пользователя
        """

        data = {
            'username': username,
            'password': password,
            'return_url': '/'
        }
        
        # создание пользовательской сессии
        if not self._user_sessions.get(username):
            requests_session = requests.Session()

            self._user_sessions[username] = UserSession(requests_session, data)

        user_session: UserSession = self._user_sessions[username]

        # TODO: добавить поддержку разных городов, на данный момент поддерживается
        # только NN, из-за domain=nnov0773, сделать автоопределение domain
        #                                                |################|
        auth_url = f'https://edu.gounn.ru/?user={username}&domain=nnov0773'

        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            '(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        )

        # задаю user-agent (индентификатор) сессии
        user_session.requests_session.get(
            auth_url,
            headers = {
                'User-Agent': user_agent
            }
        )

        # обновляю
        user_session.requests_session.headers.update({'Referer': auth_url})
        user_session.requests_session.headers.update({'User-Agent': user_agent})

        #TODO: ссылаюсь к предыдущему                                     |#################|
        data['_xsrf'] = user_session.requests_session.cookies.get('_xsrf', domain="nnov0773")

        # login
        response = user_session.requests_session.post(auth_url, data=data)

        if response.status_code != eStatusCode.NORMAL.value:
            self._logger.error(f'user::{username} - не удалось войти в аккаунт (не правильный логин или пароль)')

        return User(username, self)

    async def new_user_session(self, username: str, password: str):
        """ Псевдоним для auth

            Аргументы:
                username: str -- Логин пользователя
                password: str -- Логин пользователя
        """

        await self.auth(username, password)

    def get_user_session(self, username: str) -> UserSession:
        """ Возвращает сессию пользователя

            Возвращает None если такой сессии не существует
        
            Аргументы:
                username: str -- Логин пользователя
        """

        if not self._user_sessions.get(username):
            return None

        return self._user_sessions[username]

    def get_user(self, username) -> User:
        """ Получение объекта пользователя

            Аргументы:
                username: str -- Логин пользователя
        """

        return User(username, self)

    async def get_user_week(self, username: str, offset: int=0) -> Week:
        """ Данные о учебной неделе пользователя

            Возвращает словарь с объектами Day

            Аргументы:
                username: str -- Логин пользователя
                offset: int -- смещение недели (0 - текущая, 1 - предыдущая, -1 - следующая соотв.) 
                        и т.д (неограниченное смещение) : (по умолчанию 0)
        """

        user_session = self.get_user_session(username)

        week_url = f'https://edu.gounn.ru/journal-app/u.1547/week.{offset}'

        response = user_session.requests_session.get(
            url=week_url,
            data=user_session.data
        )

        soup = BeautifulSoup(response.text, 'lxml')

        DAY_CLASS               = 'dnevnik-day'
        LESSON_CLASS            = 'dnevnik-lesson'
        LESSON_MARK_CLASS       = 'dnevnik-mark'
        DAY_TITLE_CLASS         = DAY_CLASS + '__title'
        LESSON_TIME_CLASS       = LESSON_CLASS + '__time'
        LESSON_INDEX_CLASS      = LESSON_CLASS + '__number--time'
        LESSON_HOMETASK_CLASS   = LESSON_CLASS + '__hometask'
        LESSON_TASK_CLASS       = LESSON_CLASS + '__task'
        LESSON_MARK_VALUE_CLASS = LESSON_MARK_CLASS + '__value'

        week = {}

        for day in soup.find_all('div', class_=DAY_CLASS):
            current_day = Day()

            day_title = day.find('div', class_=DAY_TITLE_CLASS).text

            current_day.title = utils.normalize_string(day_title)
            day_title_copy = current_day.title # для последующего среза в date

            current_day.title = current_day.title[:-7]
            current_day.date = day_title_copy[-5:]

            for lesson in day.find_all('div', class_=LESSON_CLASS):
                current_lesson = Lesson()

                lesson_index = lesson.find('div', class_=LESSON_INDEX_CLASS)

                # Если пустой индекс (да такое бывает)
                if lesson_index:
                    current_lesson.index = utils.normalize_string(lesson_index.text)

                lesson_title = lesson.find_all('span')

                if lesson_title:
                    for title in lesson_title:
                        current_lesson.title += utils.normalize_string(title.text)

                lesson_time = lesson.find('div', class_=LESSON_TIME_CLASS)

                if lesson_time:
                    current_lesson.time = utils.normalize_string(lesson_time.text)

                lesson_hometask = lesson.find('div', class_=LESSON_HOMETASK_CLASS)

                if lesson_hometask:
                    lesson_task = lesson_hometask.find_all('div', class_=LESSON_TASK_CLASS)

                    for task in lesson_task:
                        current_lesson.task += utils.normalize_string(task.text) + ' '

                
                lesson_marks = lesson.find('div', class_=LESSON_MARK_CLASS)

                if lesson_marks:
                    lesson_marks_value = lesson_marks.find('div', class_=LESSON_MARK_VALUE_CLASS)

                    lesson_marks_value = lesson_marks_value.get('value')

                    lesson_marks_value = utils.normalize_marks(lesson_marks_value)

                    for mark in lesson_marks_value:
                        current_lesson.marks.append(mark)

                current_day.lessons.append(current_lesson)
            
            week[current_day.title] = current_day

        # для сообщения между классами
        week['eduApiObject'] = self
        week['username'] = username

        return Week(week)

    async def get_current_user_day(self, username: str) -> Day:
        """ Возвращает объект текущего дня недели

            Аргументы:
                username: str -- Логин пользователя
        """

        week = await self.get_user_week(username, 0)

        for day in week:
            # В class day хранится date в формате 00.00 (day, month)
            current_datetime = datetime.datetime.strptime(day.date, "%d.%m")

            # Если дни совпали
            if current_datetime.day == datetime.datetime.now().day:
                return day

    async def get_user_quarter(self, username: str, quarter: int=0) -> Quarter:
        """ Возвращает оценки за текущую четверть (class Quarter)
        
            Аргументы:
                username: str -- Логин пользователя
                quarter: int -- Номер четверти (от 1 до 4) * [0 это текущая четверть]
        """

        quarter_url = f'https://edu.gounn.ru/journal-student-grades-action/u.1547{quarters[quarter]}'

        user_session = self.get_user_session(username)

        response = user_session.requests_session.get(url=quarter_url, data=user_session.data)

        soup = BeautifulSoup(response.text, 'lxml')

        lessons = {}

        LESSON_NAME_CLASS   = 'text-overflow lhCell offset16'
        MARKS_COLUMN_CLASS  = 'cells_marks'
        MARK_CLASS          = 'cell'
        MARK_DATA_CLASS     =  MARK_CLASS + '-data'
        QUARTER_CLASS       = 'navigation-tabs-label add-context'

        # сначала формирую словарь названий предметов
        for lesson in soup.find_all('div', class_=LESSON_NAME_CLASS):
            if not lessons.get(lesson.text):
                lessons[lesson.text] = BaseLesson()

        for lesson_column in soup.find_all('div', class_=MARKS_COLUMN_CLASS):
            for mark_y in lesson_column.find_all('div', class_=MARK_CLASS):
                lesson_name = mark_y.get('name')

                if not lesson_name:
                    continue

                if not lessons.get(lesson_name):
                    lessons[lesson_name] = BaseLesson()

                lessons[lesson_name].title = lesson_name

                mark = mark_y.find('div', class_=MARK_DATA_CLASS)

                mark = mark.text

                # удаляю пустые клетки
                mark = mark.replace(u'\xa0', u'')

                if mark and mark != '':
                    marks = utils.normalize_marks(mark)

                    for mark in marks:
                        lessons[lesson_name].marks.append(mark)

        quarter_name = soup.find('span', class_=QUARTER_CLASS).text

        return Quarter(list(lessons.values()), quarter_name) 

    async def get_current_quarter(self) -> Quarter:
        """ Возвращает объект текущей четверти """

        quarter = await self.get_user_quarter(self.username, 0)

        return quarter

    async def logout(self, username: str):
        """ Удаление сессии пользователя

            Аргументы:
                username: str -- Логин пользователя
        """

        if not self._user_sessions.get(username):
            return

        self._user_sessions[username].requests_session.close()

        del self._user_sessions[username]

