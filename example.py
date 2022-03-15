import asyncio

from eduapi import EduApi


async def main():
    api = EduApi()
    
    await api.auth('username', 'password')
    week = await api.get_user_week('username')
    

loop = asyncio.get_event_loop()
task = loop.create_task(main())
loop.run_until_complete(task)
