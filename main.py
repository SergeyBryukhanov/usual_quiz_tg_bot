import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from quiz_data import quiz_data
from db_methods import *
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

API_TOKEN = '7313946831:AAGxPRX5mdM3ufimAeO_P0R1TI2MV9GfcSc'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def generate_options_keyboard(answer_options, correct_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        is_correct = "1" if option == correct_answer else "0"
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"{option}_{is_correct}"))
    builder.adjust(1)
    return builder.as_markup()


async def db_update(current_question_index, callback, correct=False):
    # Обновление номера текущего вопроса в базе данных
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_score = await get_user_score(callback.from_user.id)
    if correct:
        user_score += 1
    current_question_index += 1
    await update_quiz(callback.from_user.id, current_question_index, user_score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@dp.callback_query(lambda c: c.data.split("_")[1] == "1")
async def right_answer(callback: types.CallbackQuery):

    user_answer = callback.data.split("_")[0]
    current_question_index = await get_quiz_index(callback.from_user.id)

    await callback.message.answer(f"{user_answer} - Верно!")
    await db_update(current_question_index, callback, correct=True)


@dp.callback_query(lambda c: c.data.split("_")[1] == "0")
async def wrong_answer(callback: types.CallbackQuery):
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    user_answer = callback.data.split("_")[0]
    correct_answer = quiz_data[current_question_index]['options'][correct_option]
    await callback.message.answer(f"Неправильно. Ваш ответ: {user_answer}. Правильный ответ: {correct_answer}")
    await db_update(current_question_index, callback)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Показать счет"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(F.text == "Показать счет")
@dp.message(Command("score"))
async def cmd_score(message: types.Message):
    await message.answer("Таблица результатов")
    rows = await get_all_users_score()
    for row in rows:
        await message.answer("Участник {user_id} счет: {user_score}/10".format(user_id=row[0], user_score=row[2]))


async def get_question(message, user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    user_score = 0
    await update_quiz(user_id, current_question_index, user_score)
    await get_question(message, user_id)


@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


async def main():
    # Запускаем создание таблицы базы данных
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
