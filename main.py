from aiogram import Bot, Dispatcher, executor, types 
from aiogram.types import InputMediaPhoto, ParseMode, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Unauthorized
import asyncio
import logging
import datetime
import config
import time
from db import DB_CHENELS
from emoji import emojize


db_chennels = DB_CHENELS()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# States
class State_admin(StatesGroup):
# Log in in Bot
    logIn = State()
# Quest mode
    photo = State() 
    title = State()  
    text = State() 
    btn_text = State() 
# Add new chennels
    chennel_id = State()

@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    info = """
    Бот працює
    Введіть пароль для авторизації
    """
    await message.answer(info)



"""
CREATE QUEST BUTTON
"""

"""
MESSAGES HEDLER
"""

"""
START QUEST
- STATE: NONE -> PHOTO
- ABOUT: START CREATE POST WITH QUEST-BTN
"""

@dp.message_handler(state=State_admin.logIn, commands='quest')
@dp.message_handler(Text(equals='quest', ignore_case=True), state=State_admin.logIn)
async def cmd_start_quest(message):
    await State_admin.photo.set()
    info = """
    Режим створення посту з "квест"-кнопкою
---Для виходу введіть  "/cancel"

Для продовження завантажте фото або відео
(Для пропуску уведвіть "/next")
    """
    
    await message.answer(info)

"""
- STATE: QUEST'S STATES -> NONE
- ABOUT: EXIT FROM QUEST'S STATE
"""
@dp.message_handler(state=[State_admin.photo, State_admin.title, State_admin.text, State_admin.btn_text], commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state=[State_admin.photo, State_admin.title, State_admin.text, State_admin.btn_text])
async def cancel_handler_uqests_states(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.set_state(State_admin.logIn)
    await message.reply('Ви вийшли з режиму створення посту з "квест"-кнопкою', reply_markup=types.ReplyKeyboardRemove())


"""
- STATE: PHOTO -> TITLE
- ABOUT: SKIP UPLOAD PHOTO/VIDEO
"""
@dp.message_handler(state=State_admin.photo, commands='next')
@dp.message_handler(Text(equals='next', ignore_case=True), state=State_admin.photo)
async def next_hendler(message: types.Message, state: FSMContext):
    await state.set_state(State_admin.title)
    info = """
    Завантаження фото або відео пропущено

Введіть заголовок посту

---Для виходу введіть  "/cancel"
    """
    await message.reply(info)

"""
- STATE: PHOTO -> PHOTO
- ABOUT: INVALID CONTENT TYPE
"""
@dp.message_handler(lambda message: message.photo == [] and message.video is None, state=State_admin.photo)
async def invalid_upload_phtot_video_handler(message: types.Message, state: FSMContext):
    info = f"""
    Некоректне повідомлення

Завантажте фото або відео

---Для виходу введіть  "/cancel"
    """
    await message.answer(info)


"""
- STATE: PHOTO -> TITLE
- ABOUT: UPLOAD PHOTO/VIDEO
"""
@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.VIDEO], state=State_admin.photo)
async def upload_photo_video_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.video is None:
            data['photo'] = message.photo[0]
            temp  = "Фото"
        else:
            data['video'] = message.video[0]
            temp  = "Відео"
            
    info = f"""
    {temp} завантажено

Введіть заголовок посту

---Для виходу введіть  "/cancel"
    """
    await state.set_state(State_admin.title)  
    await message.answer(info)

"""
- STATE: TITLE -> TITLE
- ABOUT: INVALID CONTENT TYPE
"""

@dp.message_handler(lambda message: message.text is None, content_types=ContentType.ANY, state=State_admin.title)
async def invalid_title_handler(message: types.Message,  state: FSMContext):
    info = f"""
    Некоректне повідомлення

Ведіть заголовок посту

---Для виходу введіть  "/cancel"
    """
    await message.answer(info)

"""
- STATE: TITLE -> TEXT
- ABOUT: SET POSTS'S TITLE
"""
@dp.message_handler(state=State_admin.title)
async def title_handler(message: types.Message, state: FSMContext):
    if len(message.text) > 120:
        info = f"""
        Завелика кількість символів\n(маскимум: 900, в цьому тексті {len(message.text)})\n\n---Для виходу введіть  "/cancel"
        """
    else: 
        info = """
        Заголовок посту збережено\n\nВведіть текст посту\n\n---Для виходу введіть  "/cancel"
        """
        async with state.proxy() as data:
            data['title'] = message.text
        await state.set_state(State_admin.text) 
    await message.answer(info)

"""
- STATE: TEXT -> TEXT
- ABOUT: INVALID CONTENT TYPE
"""

@dp.message_handler(lambda message: message.text is None, content_types=ContentType.ANY, state=State_admin.text)
async def invalid_text_handler(message: types.Message,  state: FSMContext):
    info = """
    Некоректне повідомлення

Ведіть текст посту

---Для виходу введіть  "/cancel"
    """
    await message.answer(info)

"""
- State: TEXT -> BTN_TEXT
- About: SET POST'S TEXT
"""
@dp.message_handler(state=State_admin.text)
async def text_handler(message: types.Message, state: FSMContext):
    if len(message.text) > 900:
        info = f"""
        Завелика кількість символів\n(маскимум: 900, в цьому тексті {len(message.text)})\n\n---Для виходу введіть  "/cancel"
        """
    else: 
        info = """
        Текст посту збережено\n\nВведіть текст "квест"-кнопки\n\n---Для виходу введіть  "/cancel"
        """
        async with state.proxy() as data:
            data['text'] = message.text
        await state.set_state(State_admin.btn_text)   
    await message.answer(info)

"""
- STATE: BTN_TEXT -> BTN_TEXT
- ABOUT: INVALID CONTENT TYPE
"""

@dp.message_handler(lambda message: message.text is None, content_types=ContentType.ANY, state=State_admin.text)
async def invalid_btn_text_handler(message: types.Message,  state: FSMContext):
    info = f"""
    Некоректне повідомлення

Ведіть текст посту

---Для виходу введіть  "/cancel"
    """
    await message.answer(info)

"""
- State: BTN_TEXT -> BTN_TEXT
- About: SET BTN'S TEXT
"""
@dp.message_handler(state=State_admin.btn_text)
async def btn_text_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['btn_text'] = message.text
        info = """Текст кнопки збережено\n\nПопередній перегляд посту через 2 секунди:\n(Для опублікування нажміть кнопку під постом)\n\n---Для виходу введіть  "/cancel" """   
        await message.answer(info)
        time.sleep(2) 
        text = f"""<b>{data['title']}</b>\n\n{data['text']}"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(data['btn_text'], callback_data='subcribe'))
        for channel in db_chennels.chennels:
            keyboard.add(InlineKeyboardButton(f"Опублікувати в {channel}", callback_data=f"publish+{channel}"))
        keyboard.add(InlineKeyboardButton(emojize(":x: Завершити", use_aliases=True), callback_data='exit'))
        if 'photo' in data:
            await message.answer_photo(data['photo']['file_id'], caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        elif 'video' in data:
            await message.answer_video(data['video']['file_id'], caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        else:
            await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

"""
CALLBACK_QUERY_HANDLER
"""
"""
- State: BTN_TEXT -> None
- About: PUBLISH POST WITH QUEST BTN
"""
@dp.callback_query_handler(lambda call: 'publish' in call.data , state=State_admin.btn_text)
async def callback_publish(call: types.CallbackQuery, state: FSMContext):
    _, channel_id = call.data.split('+')
    async with state.proxy() as data:
        text = f"""<b>{data['title']}</b>\n\n{data['text']}"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(data['btn_text'], callback_data='subcribe'))
        try:
            if 'photo' in data:
                await bot.send_photo(channel_id, data['photo']['file_id'], caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            elif 'video' in  data:
                await bot.send_video(channel_id,data['video']['file_id'], caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            else:
                await bot.send_message(channel_id,text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            
            await bot.answer_callback_query(call.id, f"Опубліковано в {channel_id}")
        except Unauthorized as ex:
            await bot.answer_callback_query(call.id, f"Неопубліковано в {channel_id}\nБот не є АДМІНОМ каналу")

"""
- State: BTN_TEXT -> None
- About: EXIT FROM QUEST MODE
"""
@dp.callback_query_handler(lambda call: call.data == 'exit' , state=State_admin.btn_text)
async def callback_exit(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(State_admin.logIn)
    info = """
    /quest - створити пост з "Квест" кнопкою
/add_chennel - додати новий канал
/exit - вийти з боту
    """
    await bot.answer_callback_query(call.id, "Завершено")
    await bot.send_message(call.message.chat.id, info)


"""
- State: None
- About: CHECK USER SUBCRIBE
"""

@dp.callback_query_handler(lambda call: call.data == 'subcribe', state = '*')
async def callback_subcribe(call: types.CallbackQuery):
    status = ['creator', 'administrator', 'member']
    for chri in status:
        current_status = await bot.get_chat_member(chat_id=call.message.chat.id, user_id=call.from_user.id)
        if chri == current_status['status']:
            await bot.answer_callback_query(call.id, 'Полное видео на 3 поста выше :)', show_alert=True)
    await bot.answer_callback_query(call.id, 'Для полного просмотра нужно подписаться на канал', show_alert=True)



"""
ADD NEW CHENNELS
"""

"""
MESSAGES HEDLER
"""

"""
START ADD NEW CHENNEL
- STATE: None -> CHENNEL_ID
- ABOUT: START ADD NEW CHENNEL
"""
@dp.message_handler(state = State_admin.logIn, commands=['add_chennel'])
async def cmd_start_add_new_chennel(message: types.Message, state: FSMContext):
    await state.set_state(State_admin.chennel_id)
    info = """
    Режим додавання нового каналу додавання постів з "квест" кнопкою
    ---Для виходу введіть  "/cancel"

Для продовження вставте посилання на телеграм канал
(Наприклад: https://t.me/examplechennel)
    """
    await message.answer(info)

"""
- STATE: CHANNEL'S STATES -> NONE
- ABOUT: EXIT FROM CHANNEL'S STATE
"""
@dp.message_handler(state=State_admin.chennel_id, commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state=State_admin.chennel_id)
async def cancel_handler_chennels_states(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.set_state(State_admin.logIn)
    await message.reply('Ви вийшли з режиму додавання телеграм каналу', reply_markup=types.ReplyKeyboardRemove())

"""
- STATE: CHENNEL_ID -> CHENNEL_ID
- ABOUT: INVALID CONTENT TYPE
"""
@dp.message_handler(lambda message: 'https://t.me/' not in message.text , state=State_admin.chennel_id)
async def invalid_add_new_chennel_handler(message: types.Message, state: FSMContext):
    info = f"""
    Некоректне формат посилання

Для продовження вставте посилання на телеграм канал
(Наприклад: https://t.me/examplechennel)

---Для виходу введіть  "/cancel"
    """
    await message.answer(info)

"""
- STATE: CHENNEL_ID -> CHENNEL_ID
- ABOUT: START ADD NEW CHENNEL
"""
@dp.message_handler(lambda message: 'https://t.me/' in message.text, state=State_admin.chennel_id)
async def cmd_add_chennel_link(message: types.Message, state: FSMContext):

    new_chennel = '@' + message.text.split('https://t.me/')[1]
    db_chennels.add_new_chennel_to_list(new_chennel)
    
    
    await state.set_state(State_admin.logIn)
            
    info = """
    Посилання на канал успішно доданно
Ви вийшли з режиму додавання телеграм каналів

"""
    await message.answer(info) 

"""
LOG IN
"""

"""
MESSAGES HEDLER
"""

"""
START lOG IN
- STATE: NONE -> LOGIN
- ABOUT: RECIEVE PASSWORD
"""
@dp.message_handler()
async def cmd_logIn(message: types.Message, state: FSMContext):
    info_True = """
    Авторизація успішна

/quest - створити пост з "Квест" кнопкою
/add_chennel - додати новий канал
/exit - вийти з боту
    """
    info_False = """
    Пароль невірний, спробуйте ще раз.
    """
    if message.text == config.PASSWORD_TO_BOT:
        await State_admin.logIn.set()
        await message.answer(info_True)
        return
    await message.answer(info_False)

"""
- STATE: LOGIN -> NONE
- ABOUT: RECIEVE EXIT
"""
@dp.message_handler(state = State_admin.logIn, commands = ['exit'])
@dp.message_handler(Text(equals='exit', ignore_case=True), state=State_admin.logIn)
async def cmd_exit(message: types.Message, state: FSMContext):
    await state.finish()
    info = """
    Сеанс закінченно
Для входу введіть пароль
    """
    await message.answer(info)

"""
- STATE: LOGIN -> LOGIN
- ABOUT: RECIEVE ANY MESSAGES
"""
@dp.message_handler(state = State_admin.logIn)
async def cmd_any_after_logIn(message: types.Message):
    info = """
    /quest - створити пост з "Квест" кнопкою
/add_chennel - додати новий канал
/exit - вийти з боту
    """
    await message.answer(info)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)