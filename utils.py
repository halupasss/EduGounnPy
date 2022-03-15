

def normalize_string(source: str) -> str:
    """ Приводит строку из браузера в нормальный вид

        Удаляет все вертикальные отступы, лишние пробелы и т.д

        Возвращает строку в нормальном виде

        Aргументы:
            source: str -- Исходная строка
    """

    source = source.replace('\n', '')
    source = source.strip()

    return source


def normalize_marks(marks: str) -> list:
    """ Приводит оценки в нормальный вид

        Удаляет все лишние символы

        Если гений на учителе выставил две оценки одной

        То функция разделит числа

        Аргументы:  
            marks: str -- Исходная строка с оценками
    """

    result_marks = []

    for letter in marks:
        if letter.isdigit() and letter != '/':
            result_marks.append(int(letter))

    return marks