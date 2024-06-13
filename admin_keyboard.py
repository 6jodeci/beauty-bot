from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from const import *

kb = [
    [
        KeyboardButton(text=create_service_group_button),
        KeyboardButton(text=create_item_group_button),
    ],
    [
        KeyboardButton(text=create_service_button),
        KeyboardButton(text=create_item_button),
    ],
    [KeyboardButton(text=items_button), KeyboardButton(text=service_button)],
    [KeyboardButton(text= user_booking_button)],
]

admin_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

kb = [
    [
        KeyboardButton(text=create_button),
        KeyboardButton(text=edit_button),
    ],
    [KeyboardButton(text=delete_button)],
    [KeyboardButton(text=main_menu_button)],
]

edit_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
