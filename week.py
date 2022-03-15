from day import Day


class Week:
    """ словарь в класс (думаю так удобнее) """

    def __init__(self, week: dict):
        self.week = week

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
