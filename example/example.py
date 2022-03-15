import asyncio
from eduapi import EduApi


async def main():
    # различные примеры по применению
    api = EduApi()

    user = await api.auth('username', 'password')

    # Вывод уроков в понедельник
    week = await user.get_week()

    print(week.monday.lessons)

    # вывод текущего дня
    day = await user.get_current_day()

    print(day)

    # Вывод прошлой недели

    week = await user.get_week(1)

    print(week)

    # получение оценок за текущую четверть
    quarter = await user.get_current_quarter()

    print(quarter.title)

    for lesson in quarter:
        print(lesson.title, lesson.marks)

    # получение оценок за первую четверть

    quarter = await user.get_quarter(1)

    for lesson in quarter:
        print(lesson.title, lesson.marks)


loop = asyncio.get_event_loop()
task = loop.create_task(main())

loop.run_until_complete(task)