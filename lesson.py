

class Lesson:
    time: str
    index: str
    title: str
    task: str
    marks: list[int]

    def __init__(self):
        self.time = ''
        self.index = ''
        self.title = ''
        self.task = ''
        self.marks = []
