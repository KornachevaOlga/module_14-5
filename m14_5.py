from config import *  # api
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *
import asyncio

ENG_ALPHA = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]
products = get_all_products()
api = '8100052333:AAEPovvXmKIg0JGeyWxF8WR-oxVQsuQX96E'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
rkb = ReplyKeyboardMarkup([
    [
        KeyboardButton('Рассчитать'),
        KeyboardButton('Информация')
    ], [
        KeyboardButton('Купить'),
        KeyboardButton('Регистрация')
    ]
], resize_keyboard=True)
ikb_calories = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'),
    InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
]], resize_keyboard=True)
ikb_products = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(product[1], callback_data='product_buying') for product in products]
], resize_keyboard=True)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


@dp.message_handler(text='Информация')
async def get_info(message):
    info = ('Программа расчёта количества килокалорий в сутки для Вас.\n'
            'Используется упрощённая формула Миффлина-Сан Жеора.\n'
            'Ограничения:\nвозраст — 13–80 лет,\nрост — от 140 см,\nвес — от 40 кг.')
    await message.answer(info, reply_markup=rkb)


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=rkb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=ikb_calories)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Для мужчин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (г) + 5\n'
                              'Для женщин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (г) - 161')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    try:
        if int(message.text) < 13 or int(message.text) > 80:
            raise ValueError()
    except ValueError:
        await message.answer('Ошибка! Формула применима для лиц в возрасте от 13 до 80 лет.\nВведите свой возраст:')
        await UserState.age.set()
    else:
        await state.update_data(age=message.text)
        await message.answer('Введите свой рост (в сантиметрах):')
        await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    try:
        if int(message.text) < 140:
            raise ValueError()
    except ValueError:
        await message.answer('Ошибка! Нижняя граница роста — 140 см.\nВведите свой рост (в сантиметрах):')
        await UserState.growth.set()
    else:
        await state.update_data(growth=message.text)
        await message.answer('Введите свой вес (в килограммах):')
        await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_gender(message, state):
    try:
        if int(message.text) < 40:
            raise ValueError()
    except ValueError:
        await message.answer('Ошибка! Нижняя граница веса — 40 кг.\nВведите свой вес (в килограммах):')
        await UserState.weight.set()
    else:
        await state.update_data(weight=message.text)
        await message.answer('Введите свой пол (М / Ж):')
        await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def send_calories(message, state):
    if message.text.upper() == 'М':
        rg = 5
    elif message.text.upper() == 'Ж':
        rg = -161
    else:
        await message.answer('Ошибка!\nВведите свой пол (М / Ж):')
        await UserState.gender.set()
        return
    await state.update_data(gender=message.text)
    data = await state.get_data()
    result = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + rg
    await message.answer(f'Количество килокалорий в сутки для Вас: {result}')
    await state.finish()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for product in products:
        await message.answer(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
        with open(f'цветы{product[0]}.png', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=ikb_products)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


def is_eng_alpha(text):
    if not isinstance(text, str):
        return False
    for a in text:
        if a not in ENG_ALPHA:
            return False
    return True


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_eng_alpha(message.text):
        await message.answer('Введите имя пользователя (только латинский алфавит):')
        await RegistrationState.username.set()
    elif is_included(message.text):
        await message.answer(f'Пользователь {message.text} существует. Введите другое имя (только латинский алфавит):')
        await RegistrationState.username.set()
    else:
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    try:
        if int(message.text) < 18:
            await message.answer('Извините, но нашими покупателями могут быть только лица, достигшие возраста 18 лет.')
            await state.finish()
            return
    except ValueError:
        await message.answer('Ошибка ввода: ожидается число.\nВведите свой возраст:')
        await RegistrationState.age.set()
    else:
        await state.update_data(age=message.text)
        data = await state.get_data()
        add_user(data['username'], data['email'], data['age'])
        await message.answer('Регистрация прошла успешно.')
        await state.finish()


@dp.message_handler()
async def all_massages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)