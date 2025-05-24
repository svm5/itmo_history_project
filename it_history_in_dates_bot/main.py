import os
import datetime

import asyncio

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import Database
from mailing import remind

from pprint import pprint

import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

token =  os.getenv("TOKEN")
bot = Bot(token)
dp = Dispatcher(bot=bot)
router = Router()

db = Database()

async def on_startup():
    print("Start Bot!")
    await db.async_init()
    print("ok")

async def on_shutdown():
    print("Bot stopped")

def create_story_reply_markup(next_story_id: int):
    if next_story_id is None:
        return None
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Следующая часть",
        callback_data=f"story_{next_story_id}")
    )

    return builder.as_markup()

def create_question_reply_markup(quiz_id: int, number: int, correct_cnt: int, answers):
    builder = InlineKeyboardBuilder()
    for answer in answers:
        builder.row(InlineKeyboardButton(
            text=answer[1],
            callback_data=f"answer_{quiz_id}_{number}_{correct_cnt}_{answer[0]}")
        )

    return builder.as_markup()

async def send_summary(chat_id: int, quiz_id: int, correct_cnt: int):
    await bot.send_message(chat_id, text=f"Квиз окончен! Правильных ответов: {correct_cnt}/{len(await db.get_questions_by_quiz_id(quiz_id))}")

async def send_question(chat_id: int, quiz_id: int, correct_cnt: int, question_number: int):
    q = await db.get_question_by_quiz_id_and_number(quiz_id, question_number)
    if q == None:
        await send_summary(chat_id, quiz_id, correct_cnt)
        return
    
    q_id, q_description = int(q[0]), q[1]
    answers = await db.get_answers_by_question_id(q_id)

    await bot.send_message(chat_id, text=f"Вопрос {question_number}. " + q_description, reply_markup=create_question_reply_markup(quiz_id, question_number, correct_cnt, answers))


async def send_story(chat_id: int, story_id: int):
    story_data = await db.get_story(story_id)
    text = story_data[1]
    markup = None
    if story_data[2] == None:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

        stories_list_id = int(story_data[3])
        quiz_id = int((await db.get_quiz_id_by_stories_list_id(stories_list_id))[0])
        if quiz_id != None:
            await send_question(chat_id, quiz_id, 0, 1)
    else:
        next_id = int(story_data[2])
        markup=create_story_reply_markup(next_id)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

async def is_correct_answer(answer_id):
    answer = await db.get_answer_by_id(answer_id)

    return answer[3]

async def get_correct_answers(quiz_id: int, question_number: int):
    q = await db.get_question_by_quiz_id_and_number(quiz_id, question_number)
    return ", ".join([x[1] for x in(await db.get_correct_answer_by_question_id(int(q[0])))])

@router.message(Command("start"))
async def start(message: Message):
    pprint(message)
    chat_id = message.chat.id
    username = None
    try:
        username = message.chat.username
    except:
        print("No username")
    current_time = datetime.datetime.now()
    user = await db.find_user_by_id(chat_id)
    print("User", user)
    if user is None:
        await db.add_user(chat_id, username, current_time)

    await bot.send_message(chat_id=chat_id, text="Привет!\nЯ расскажу о том, как развивались информационные технологии в XX веке. После этого ты сможешь пройти квиз, а также получать рассылку")
    await send_story(chat_id, 1)

@router.callback_query(F.data.startswith("story_"))
async def story_handler(call: CallbackQuery):
    _, next_story_id = call.data.split("_")
    await call.answer("")
    await send_story(call.message.chat.id, int(next_story_id))

@router.callback_query(F.data.startswith("answer_"))
async def question_handler(call: CallbackQuery):
    _, quiz_id, question_number, correct_cnt, answer_id = call.data.split("_")
    correct_cnt = int(correct_cnt)
    reply_text = "Правильный ответ!"
    if await is_correct_answer(int(answer_id)):
        correct_cnt += 1
    else:
        reply_text="К сожалению, вы ошиблись. Правильный ответ: " + await get_correct_answers(quiz_id, question_number)
    await call.answer("")
    await bot.send_message(call.message.chat.id, text=reply_text)
    await send_question(call.message.chat.id, int(quiz_id), correct_cnt, int(question_number) + 1)

dp.include_router(router)

async def start_app():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    scheduler.start()
    await dp.start_polling(bot)

scheduler = AsyncIOScheduler()
scheduler.add_job(remind, 'cron', hour=17, minute=58, args=[bot])
# scheduler.add_job(f, 'interval', minutes=1, next_run_time=datetime.datetime.now())

if __name__ == "__main__":
    print("here")
    asyncio.run(start_app())
