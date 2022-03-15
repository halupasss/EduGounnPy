from lesson import Lesson


class Day:
    title: str = ''
    lessons: list[Lesson]
    date: str

    def __init__(self):
        self.title = ''
        self.lessons = []
        self.date = ''

    def __str__(self):
        return self.date + ' ' + self.title + str([str(self.lessons[i]) for i in range(len(self.lessons))])