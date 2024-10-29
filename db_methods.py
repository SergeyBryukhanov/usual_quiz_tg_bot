import aiosqlite

DB_NAME = 'quiz_bot.db'


async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_quiz(user_id, index, user_score):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, user_score) VALUES (?, ?, ?)',
                         (user_id, index, user_score))
        # Сохраняем изменения
        await db.commit()


async def get_user_score(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT user_score FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


# async def update_user_score(user_id, user_score):
#     # Создаем соединение с базой данных (если она не существует, она будет создана)
#     async with aiosqlite.connect(DB_NAME) as db:
#         # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
#         await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, user_score) VALUES (?, ?)',
#                          (user_id, user_score))
#         # Сохраняем изменения
#         await db.commit()


async def get_all_users_score():
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем счёт всех пользователей
        async with db.execute('SELECT * FROM quiz_state') as cursor:
            # Возвращаем результат
            rows = await cursor.fetchall()
            if rows is not None:
                return rows
            else:
                return 0


async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, 
                         question_index INTEGER, user_score INTEGER)''')
        # Сохраняем изменения
        await db.commit()
