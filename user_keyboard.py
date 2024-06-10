from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

kb = [
        [KeyboardButton(text='Товары'),
        KeyboardButton(text='Услуги')],
        [KeyboardButton(text='Где мы находимся?'),
        KeyboardButton(text='Поддержка')],
]

start_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

kb = [
        [KeyboardButton(text="Женский зал"),
        KeyboardButton(text="Общий зал"),
        KeyboardButton(text="Мужской зал")],
        [KeyboardButton(text="На главную")]
]

hall_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

kb = [
        [KeyboardButton(text='Создать группу услуг'),
        KeyboardButton(text='Создать группу товаров'),]
        [KeyboardButton(text='Создать услугу'),
        KeyboardButton(text='Создать товар')]
        [KeyboardButton(text='Товары'),
        KeyboardButton(text='Услуги')],
        [KeyboardButton(text='Где мы находимся?'),
        KeyboardButton(text='Поддержка')],
]

admin_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)