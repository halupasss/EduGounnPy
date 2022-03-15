

from unittest.mock import Base


class BaseLesson:
    title: str
    marks: list[int]

    def __init__(self):
        self.title = ''
        self.marks = []

    def __str__(self):
        return self.title + str(self.marks)


class Lesson(BaseLesson):
    time: str
    index: str
    task: str

    def __init__(self):
        self.time = ''
        self.index = ''
        self.task = ''

    def __str__(self):
        return self.time + ' ' + self.index + ' ' + self.title + str(self.marks) + self.task
