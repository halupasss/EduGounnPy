from user_session import UserSession
from day import Day
from lesson import Lesson


class User:
    pass


class Week:
    """ словарь в класс (думаю так удобнее) """

    def __init__(self, week: dict):
        self.week = week

        self.current_index = 0

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

    @property
    def user(self) -> User:
        """ Возвращает объект пользователя User """

        return User(self.week['username'], self.week['eduApiObject'])

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


class Quarter:
    lessons: list[Lesson]
    title: str

    def __init__(self, lessons: list[Lesson], title: str):
        self.lessons: list[Lesson]  = lessons
        self.title: str             = title

    def __str__(self):
        return str(self.lessons)

    def __getitem__(self, key):
        return self.lessons[key]


class User:
    user_session: UserSession

    user_real_name: str
    user_school: str
    user_city: str

    def __init__(self, username: str, eduapi):
        self.user_session = None
        self.user_real_name = ''
        self.user_school = ''
        self.user_city = ''
        
        self.username = username

        self._api = eduapi

        self.user_session = self._api.get_user_session(username)

    async def get_week(self, offset: int=0) -> Week:
        """ Псевдоним для EduApi.get_user_week()

            Аргументы:
                offset: int -- Смещение недели (подробнее в документации EduApi.get_user_week())
        """
        week = await self._api.get_user_week(self.username, offset)

        return week

    async def get_current_day(self) -> Day:
        """ Псевдоним для EduApi.get_current_user_day() """

        day =  await self._api.get_current_user_day(self.username)

        return day

    async def get_quarter(self, quarter: int=0) -> Quarter:
        """ Псевдоним для EduAi.get_user_quarter() """

        quarter = await self._api.get_user_quarter(self.username, quarter)

        return quarter

    async def get_current_quarter(self) -> Quarter:
        """ Возвращает объект текущей четверти """

        quarter = await self._api.get_user_quarter(self.username, 0)

        return quarter

    def __str__(self):
        return self.username

