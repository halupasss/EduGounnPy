

from matplotlib.pyplot import title
from lesson import Lesson


class Day:
    title: str = ''
    lessons: list[Lesson]
    date: str

    def __init__(self):
        self.title = ''
        self.lessons = []
        self.date = ''