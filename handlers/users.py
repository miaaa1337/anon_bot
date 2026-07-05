import time
from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram import F
import asyncpg
from config import MY_ID, CHANNEL_ID
router = Router()

last_admin_notification_time = {}
last_channel_notification_time = {}
spam_tracker = {}
banned_words_cache = set()

async def load_banned_words(db_pool: asyncpg.Pool):
    global banned_words_cache
    async with db_pool.acquire() as connection:
        rows = await connection.fetch("SELECT word FROM banned_words;")
        banned_words_cache = {row['word'] for row in rows}
    print(f"✅ Кэш запрещенных слов успешно загружен! Всего слов: {len(banned_words_cache)}")



@router.message(Command("start"))
async def start_cmd(message: types.Message, db_pool: asyncpg.Pool):
   async with db_pool.acquire() as connection:
     await connection.execute(
            """
            INSERT INTO users (telegram_id, username) 
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET username = EXCLUDED.username;
            """,
            message.from_user.id, message.from_user.username
           )
   builder = ReplyKeyboardBuilder()
   
   builder.add(KeyboardButton(text="старт"))
   builder.add (KeyboardButton(text="🆘 помощь"))
   builder.add (KeyboardButton(text="правила"))
   builder.add (KeyboardButton(text="ℹ️ о боте"))
   builder.adjust(2)
   
   await message.answer("прив, это 100% анон бот для ваших гадостей и всяких сильно волнующих вопросиков! не стесняйся, задавай свои вопросы!^^", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "старт")
async def start_button(message: types.Message, db_pool: asyncpg.Pool):
    await start_cmd(message, db_pool) 

@router.message(F.text == "🆘 помощь")
async def help_buttons(message: types.Message):
    await message.answer("ты можешь написать мне любое сообщение, и я анонимно отправлю его в общий канал. \n \n " 
                         "если ты хочешь узнать о боте, используй кнопку (ℹ️ о боте). \n \n если у тебя возникли проблемы при использовании бота, напиши <i>создателю бота</i> - @miaa1337", parse_mode="HTML")

@router.message(F.text == "правила")
async def rules_buttons(message: types.Message):
    await message.answer("1. не флуди, не спамь и не пиши запрещенные слова. \n \n"
                         "2. не пытайся обмануть бота и не нарушай правила канала. \n \n "
                         "3. не используй бота для оскорблений, угроз и других незаконных действий. \n \n"
                         "4. не пытайся взломать бота или использовать его в своих целях. \n \n"
                         "5. не используй бота для рекламы и продвижения своих проектов.", parse_mode="HTML")

@router.message(F.text == "ℹ️ о боте")
async def about_buttons(message: types.Message):
    await message.answer("это <b>анонимный бот</b> для отправки анон сообщений в общий тг канал для чата execute. \n \n "
                         "бот не хранит ваши данные, анонимность гарантирована. \n \n "
                         "бот создан для раскрытия давно интригующих вопросов, для обсуждения волнующих тем и для того, чтобы вы могли анонимно высказать своё мнение.", parse_mode="HTML")

@router.message(Command("бан_слова"))
async def show_banned_words(message: types.Message):
    if message.from_user.id != MY_ID:
        return
    if not banned_words_cache:
        await message.answer("В списке запрещенных слов пока пусто.")
        return
    words_list = "\n".join(f"• {word}" for word in banned_words_cache)
    admin_help = (
        f"📝 **Текущие запрещенные слова:**\n{words_list}\n\n"
        f"⚙️ **Шпаргалка по командам:**\n"
        f"• `/добавить слово` — добавить в базу и кэш\n"
        f"• `/удалить слово` — удалить из базы и кэш"
    )
    await message.answer(admin_help, parse_mode="Markdown")




@router.callback_query(F.data.startswith("ban:"))
async def ban_user_callback(callback: types.CallbackQuery, db_pool: asyncpg.Pool):
    user_id_to_ban = int(callback.data.split(":")[1])

    async with db_pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO ban_list (telegram_id, reason, banned_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (telegram_id) DO NOTHING;
            """,
            user_id_to_ban, "забанен через админ-панель"
        )
        
    await callback.answer("Пользователь успешно забанен!")
    await callback.message.edit_text(
        f"{callback.message.text}\n\n🛑 **СТАТУС:** ЗАБАНЕН В БАЗЕ ДАННЫХ!",
        parse_mode="Markdown",
        reply_markup=callback.message.reply_markup
    )

@router.callback_query(F.data.startswith("unban:"))
async def unban_user_callback(callback: types.CallbackQuery, db_pool: asyncpg.Pool):
    user_id_to_unban = int(callback.data.split(":")[1])

    async with db_pool.acquire() as connection:
        await connection.execute(
            """
            DELETE FROM ban_list WHERE telegram_id = $1;
            """,
            user_id_to_unban
        )

    await callback.answer("Пользователь успешно разбанен!")
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ **СТАТУС:** РАЗБАНЕН В БАЗЕ ДАННЫХ!",
        parse_mode="Markdown",
        reply_markup=callback.message.reply_markup
    )

@router.message(Command("добавить"))
async def add_banned_word(message: types.Message, db_pool: asyncpg.Pool):
    if message.from_user.id != MY_ID:
        await message.answer("сначала свой бот напиши чтобы добавлять всякое сюда")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Пожалуйста, укажите слово для добавления.")
        return

    word_to_ban = args[1].strip().lower()

    async with db_pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO banned_words (word)
            VALUES ($1)
            ON CONFLICT (word) DO NOTHING;
            """,
            word_to_ban
        )

    await message.answer(f"Слово '{word_to_ban}' успешно добавлено в список запрещенных слов.")

@router.message(Command("удалить"))
async def delete_banned_word(message: types.Message, bot: Bot, db_pool: asyncpg.Pool):
    if message.from_user.id != MY_ID:
            await message.answer("недостаточно прав охаешечки")
            return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("а где слово?")
        return
    word_to_delete = args[1].strip().lower()

    async with db_pool.acquire() as connection:
        status = await connection.execute(
            """
            DELETE FROM banned_words WHERE word = $1;
            """,
            word_to_delete
        )

    if status == "DELETE 0":
        await message.answer(f"Слово '{word_to_delete}' не найдено в списке запрещенных слов.")
    else:
        await message.answer(f"Слово '{word_to_delete}' успешно удалено из списка запрещенных слов.")

@router.message(Command("стата"))
async def show_stats(message: types.Message, db_pool: asyncpg.Pool):
    if message.from_user.id != MY_ID:
        await message.answer("а-а-а эта команда только для админа!")
        return
    async with db_pool.acquire() as connection:
        total_msg = await connection.fetchval("SELECT COUNT(*) FROM messages;")
        banned_msg = await connection.fetchval("SELECT COUNT(*) FROM messages WHERE status = 'banned_word';")
        blocked_spam = await connection.fetchval("SELECT COUNT(*) FROM messages WHERE status = 'blocked_spam';")
        approved_msg = await connection.fetchval("SELECT COUNT(*) FROM messages WHERE status = 'approved';")
    stats_message = (
        f"📊 **Статистика сообщений:**\n"
        f"• всего сообщений: {total_msg}\n"
        f"• одобренные сообщения: {approved_msg}\n"
        f"• заблокированные (спам): {blocked_spam}\n"
        f"• заблокированные (запрещенные слова): {banned_msg}"
    )
    await message.answer(stats_message, parse_mode="Markdown")

@router.message ()
async def forward_to_me (message: types.Message, bot: Bot, db_pool: asyncpg.Pool):
    if message.from_user.id == 1: 
        await message.answer("это твой бот не тупи")
        return
    user_id = message.from_user.id

    msg_type = None
    content = None
    status = "approved"

    if message.text:
        msg_type = "text"
        content = message.text
    elif message.photo:
        msg_type = "photo"
        content = message.photo[-1].file_id
    elif message.video:
        msg_type = "video"
        content = message.video.file_id
    elif message.animation:
        msg_type = "animation"
        content = message.animation.file_id
    elif message.sticker:
        msg_type = "sticker"
        content = message.sticker.file_id
    elif message.document:
        msg_type = "document"
        content = message.document.file_id
    elif message.voice:
        msg_type = "voice"
        content = message.voice.file_id

    async with db_pool.acquire() as connection:
        banned_user = await connection.fetchrow(
            "SELECT telegram_id FROM ban_list WHERE telegram_id = $1",
            user_id
        )
    if banned_user:
        await message.answer("ты забанен, не пиши мне больше!")
        return

    current_time = time.time()
    if user_id not in spam_tracker:
        spam_tracker[user_id] = []

    spam_tracker[user_id] = [item for item in spam_tracker[user_id] if current_time - item["time"] < 5]
    if len(spam_tracker[user_id]) >= 2:
        for item in spam_tracker[user_id]:
           if item["msg_id"]:
              try:
                 await bot.delete_message(chat_id= CHANNEL_ID, message_id=item["msg_id"])
              except Exception:
                    pass
        spam_tracker[user_id] = []
        status = "blocked_spam"
        async with db_pool.acquire() as connection:
            await connection.execute (
                 """
                 INSERT INTO messages (type, content, status) VALUES ($1, $2, $3)""", msg_type, content, status
                                )
        await message.answer("в спаме отказано, зачиллься бурмалда")
        return

    if message.text:
        text_lower = message.text.lower()
        async with db_pool.acquire() as connection:
            rows = await connection.fetch("SELECT word FROM banned_word_cache;")
            db_banned_words = [row['word'] for row in rows]

        for word in db_banned_words:
            if word in text_lower:
                status = "banned_word"
                async with db_pool.acquire() as connection:
                        await connection.execute (
                            """
                            INSERT INTO messages (type, content, status) VALUES ($1, $2, $3)""", msg_type, content, status
                        )
                await message.answer("твоё сообщение содержит запрещённые слова и не будет отправлено.")
                return
    current_time = time.time()
    user_id = message.from_user.id
    passed_for_admin = current_time - last_admin_notification_time.get(user_id, 0)
    passed_for_channel = current_time - last_channel_notification_time.get(user_id, 0)

    if passed_for_admin > 60:
        last_admin_notification_time[user_id] = current_time
        admin_info = f"👤 **Пишет пользователь:** {message.from_user.full_name} (@{message.from_user.username or 'no username'})\n🆔 ID: {user_id}"

        inline_builder = InlineKeyboardBuilder()
        inline_builder.add(InlineKeyboardButton(
        text = "❌ Забанить", 
        callback_data = f"ban:{user_id}"
    ))
        inline_builder.add(InlineKeyboardButton(
        text ="✅ Разбанить",
        callback_data = f"unban:{user_id}"
    ))
    
        await bot.send_message(
        chat_id = MY_ID, 
        text = admin_info, 
        parse_mode = "Markdown",
        reply_markup = inline_builder.as_markup()
    )
    await message.copy_to(chat_id=MY_ID)

    history_len_before = len(spam_tracker[user_id])
    sent_msg_id = None

    if message.text:
     
     if passed_for_channel > 60:
      full_text = f"пришло новое анон сообщение:\n\n{message.text}"
      sent_msg = await bot.send_message(chat_id=CHANNEL_ID, text=full_text)
      sent_msg_id = sent_msg.message_id
      last_channel_notification_time[user_id] = current_time
     else:
       sent_msg = await bot.send_message(chat_id=CHANNEL_ID, text=message.text)
       sent_msg_id = sent_msg.message_id

    else:
        if passed_for_channel > 60:
            await bot.send_message(chat_id=CHANNEL_ID, text="пришло новое анон сообщение:", parse_mode="Markdown")
            last_channel_notification_time[user_id] = current_time
        
        sent_msg = await message.copy_to(chat_id=CHANNEL_ID)
        sent_msg_id = sent_msg.message_id
    spam_tracker[user_id].append({"time": current_time, "msg_id": sent_msg_id})
    if len(spam_tracker[user_id]) == 0 or history_len_before >= 2:
        return
    async with db_pool.acquire() as connection:
                await connection.execute (
                     """
                     INSERT INTO messages (type, content, status) VALUES ($1, $2, $3)""", msg_type, content, status
                                    )
    await message.answer("твоё сообщение успешно отправлено анонимно!")