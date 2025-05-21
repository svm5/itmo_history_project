import asyncio
import psycopg

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Database:
    def __init__(self):
        print("init")

    async def async_init(self):
        
        self.connection = await psycopg.AsyncConnection.connect(user='', 
                                                    password='', 
                                                    dbname='', 
                                                    host='',
                                                    port='')
        self.cursor = self.connection.cursor()

    
    async def find_user_by_id(self, user_id):
        print("find by id", user_id)
        await self.cursor.execute(f"""SELECT * FROM Users WHERE users.id = '{user_id}'""")
        result = await self.cursor.fetchone()
        return result
    
    async def get_all_users(self):
        await self.cursor.execute(f"""SELECT * FROM Users""")
        return await self.cursor.fetchall()
    
    async def add_user(self, user_id, username, created_at):
        await self.cursor.execute(f"""INSERT INTO users (id, username, created_at) values('{user_id}', '{username}', '{created_at}')""")
        await self.connection.commit()

    async def get_story(self, story_id):
        await self.cursor.execute(f"""SELECT id, story, id_next, stories_list_id FROM stories WHERE id='{story_id}'""")
        return await self.cursor.fetchone()
    
    async def get_quiz_id_by_stories_list_id(self, stories_list_id):
        await self.cursor.execute(f"""SELECT quizzes_id FROM stories_quizzes WHERE stories_id='{stories_list_id}'""")
        return await self.cursor.fetchone()
    
    async def get_question_by_quiz_id_and_number(self, quiz_id, number):
        await self.cursor.execute(f"""SELECT id, description FROM questions WHERE quiz_id='{quiz_id}' AND number='{number}'""")
        return await self.cursor.fetchone()
    
    async def get_questions_by_quiz_id(self, quiz_id):
        await self.cursor.execute(f"""SELECT id, description, number FROM questions WHERE quiz_id='{quiz_id}'""")
        return await self.cursor.fetchall()

    async def get_answers_by_question_id(self, question_id):
        await self.cursor.execute(f"""SELECT id, description FROM answers WHERE question_id='{question_id}'""")
        return await self.cursor.fetchall()
    
    async def get_answer_by_id(self, answer_id):
        await self.cursor.execute(f"""SELECT id, question_id, description, correct FROM answers WHERE id='{answer_id}'""")
        return await self.cursor.fetchone()
    
    async def get_correct_answer_by_question_id(self, question_id):
        await self.cursor.execute(f"""SELECT id, description FROM answers WHERE question_id='{question_id}' AND correct='true'""")
        return await self.cursor.fetchall()
    
    async def get_events_by_day_and_month(self, day: int, month: int):
        await self.cursor.execute(f"""SELECT * FROM events INNER JOIN events_sending ON events.id = events_sending.event_id WHERE extract(month FROM sending_date) = {month} AND extract(day FROM sending_date) = '{day}' AND is_active='true'""")
        return await self.cursor.fetchall()

    async def get_links_by_event_id(self, event_id: int):
        await self.cursor.execute(f"""SELECT link FROM events_links WHERE event_id='{event_id}'""")
        return await self.cursor.fetchall()
    