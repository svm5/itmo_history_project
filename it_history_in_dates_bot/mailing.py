import datetime

from db import Database

async def prepare_message(event):
    return 

async def remind(bot):
    db = Database()
    await db.async_init()

    now = datetime.datetime.now()
    users = await db.get_all_users()
    events = await db.get_events_by_day_and_month(now.day, now.month)
    data = []
    for event in events:
        txt = ""
        txt += event[1] + "\n\n"
        txt += event[2]

        links = await db.get_links_by_event_id(int(event[0]))
        if len(links) > 0:
            txt += "\n\n"
            txt += "Дополнительные ресурсы:"
            for link in links:
                txt += "\n"
                txt += link[0]
        data.append(txt)
        
    for user in users:
        for elem in data:
            await bot.send_message(int(user[0]), text=elem)
