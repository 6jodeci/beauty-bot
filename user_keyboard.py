from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from const import *

kb = [
    [KeyboardButton(text=items_button), KeyboardButton(text=service_button)],
    [KeyboardButton(text=location_button), KeyboardButton(text=support_button)],
]

start_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

kb = [
    [
        KeyboardButton(text=female_hall_button),
        KeyboardButton(text=all_hall_button),
        KeyboardButton(text=men_hall_button),
    ],
    [KeyboardButton(text=main_menu_button)],
]

hall_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

