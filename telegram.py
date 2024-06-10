import os
import mysql_db
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types.message import ContentType
from messages import *
from dispatcher import *
from user_keyboard import *
from const import *

# Получаем объект подключения к базе данных
connection = mysql_db.get_connection()

PRICES = [
    LabeledPrice(label='Тест', amount=1000),
]

avalible_services_group = []

avalible_items_group = []

avalible_hall = [
    "Мужской зал",
    "Женский зал",
    "Общий зал"
]

avalible_services = []

avalible_items = []

class RegisterUser(StatesGroup):
    full_name = State()
    email = State()
    phone_number = State()

class Support(StatesGroup):
    help_message = State()

class ChoiseService(StatesGroup):
    service_group = State()
    hall = State()
    service = State()

class ChoiseItem(StatesGroup):
    item_group = State()
    item = State()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext):
    # Проверяем, зарегистрирован ли пользователь в базе данных
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE id = %s", (message.from_user.id,))
    user = cursor.fetchone()

    if user['is_admin'] == True:
        await message.answer(admin_start_message, reply_markup=admin_kb)
        return

    # Если пользователь зарегистрирован, отправляем ему сообщение с помощью клавиатуры
    if user:
        await message.answer(start_message, reply_markup=start_kb)
    # Если пользователь не зарегистрирован, запрашиваем у него необходимые данные и сохраняем их в базе данных
    else:
        await message.answer(registration_not_found)
        await message.answer(request_username)
        await state.set_state(RegisterUser.full_name)

@dp.message(RegisterUser.full_name)
async def register_full_name(message: types.Message, state: FSMContext):
    await state.update_data({'full_name': message.text})
    await message.answer(request_email)
    await state.set_state(RegisterUser.email)

@dp.message(RegisterUser.email)
async def register_email(message: types.Message, state: FSMContext):
    await state.update_data({'email': message.text})
    await message.answer(request_phone_number)
    await state.set_state(RegisterUser.phone_number)

@dp.message(RegisterUser.phone_number)
async def register_phone_number(message: types.Message, state: FSMContext):
    await state.update_data({'phone_number': message.text})
    cursor = connection.cursor()
    data = await state.get_data()
    try:
        cursor.execute("INSERT INTO user (id, email, full_name, phone_number) VALUES (%s, %s, %s, %s)", (message.from_user.id, data['email'], data['full_name'], data['phone_number']))
        connection.commit()
        await message.answer(registration_success)
        await message.answer(start_message, reply_markup=start_kb)  # добавить отправку клавиатуры
    except Exception as e:
        connection.rollback()
        await message.answer(registration_error)

    cursor.close()
    await state.clear()

# SECTION LOCATION
@dp.message(lambda message: message.text == location_button)
async def send_location(message: Message):
    await bot.send_location(message.chat.id,
                            longitude=location_longitude,
                            latitude=location_latitude)
    await bot.send_message(message.chat.id, location_message)

# SECTION SUPPORT
@dp.message(lambda message: message.text == support_button)
async def send_message_support(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, help_message)
    await state.set_state(Support.help_message)
    
@dp.message(Support.help_message)
async def send_help_message(message: Message, state: FSMContext):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id FROM user WHERE is_admin = true ORDER BY RAND() LIMIT 1")
    admin_id = cursor.fetchone()[0]
    cursor.execute(f"SELECT full_name FROM user WHERE id = {message.from_user.id}")
    full_name = cursor.fetchone()[0]
    await bot.send_message(message.chat.id, help_response_message)
    await bot.send_message(admin_id, f'Сообщение от пользователя {full_name}: \n\n"{message.text}"\n\n@{message.from_user.username}')
    await state.clear()

# SECTION SERVICES
@dp.message(lambda message: message.text == service_button)
async def send_message_services(message: Message, state: FSMContext):
    cursor = connection.cursor()
    cursor.execute("SELECT name, description FROM service_group WHERE is_active = true AND is_deleted=false")
    service_groups = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for service_group in service_groups:
        kb_builder.button(text=service_group[0])
        avalible_services_group.append(service_group[0])
    kb_builder.button(text=main_menu_button)    
    kb_builder.adjust(3)    
    kb = kb_builder.as_markup(resize_keyboard=True)
    await bot.send_message(message.from_user.id, service_group_message, reply_markup=kb)
    await state.set_state(ChoiseService.service_group)

@dp.message(ChoiseService.service_group, F.text.in_(avalible_services_group))
async def send_message_hall(message: Message, state: FSMContext):
    await state.update_data(service_group=message.text)
    await bot.send_message(message.from_user.id, choise_hall_message, reply_markup=hall_kb)
    await state.set_state(ChoiseService.hall)

@dp.message(ChoiseService.hall, F.text.in_(avalible_hall))
async def send_message_service(message: Message, state: FSMContext):
    await state.update_data(hall=message.text)
    user_data = await state.get_data()
    cursor = connection.cursor()
    if user_data['hall'] == men_hall_button:
        cursor.execute(f"SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'male' and is_deleted = false and is_active = true and service_group_name = '{user_data['service_group']}'",)
    elif user_data['hall'] == female_hall_button:
        cursor.execute(f"SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'female' and is_deleted = false and is_active = true and service_group_name = '{user_data['service_group']}'")
    elif user_data['hall'] == all_hall_button:
        cursor.execute(f"SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'all' and is_deleted = false and is_active = true and service_group_name = '{user_data['service_group']}'")
    services = cursor.fetchall()
    if not services:
        await bot.send_message(message.from_user.id, service_empty_message)
        return
    kb_builder = ReplyKeyboardBuilder()
    for service_group in services:
        kb_builder.button(text=service_group[0])
        avalible_services.append(service_group[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await bot.send_message(message.from_user.id, service_message, reply_markup=kb)
    await state.set_state(ChoiseService.service)

@dp.message(ChoiseService.service, F.text.in_(avalible_services))
async def send_message_service_price(message: Message, state: FSMContext):
    await state.update_data(service=message.text)
    user_data = await state.get_data()

    cursor = connection.cursor()
    cursor.execute(f"SELECT name, description, price from service WHERE name = '{user_data['service']}'")
    service = cursor.fetchall()

    price = service[0][2]
    if price % 1 == 0:
        price = int(price)

    service_name = service[0][0]
    service_description = service[0][1].strip().capitalize()

    # Выбираем смайлик в зависимости от выбранного зала
    if user_data['hall'] == men_hall_button:
        emoji = '🧔'
    elif user_data['hall'] == female_hall_button:
        emoji = '👩'
    elif user_data['hall'] == all_hall_button:
        emoji = '🧔👩'

    service_message = (
        f'{emoji} {service_name}:\n\n'
        f'💭 {service_description}\n\n'
        f'💸 Цена: {price} руб.'
    )

    # Создаем Inline-кнопку "Записаться"
    booking_button_inline = InlineKeyboardButton(text="Записаться", callback_data="booking")

    # Создаем Inline-клавиатуру с кнопкой "Записаться"
    kb_inline = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[booking_button_inline]])

    # Отправляем сообщение с Inline-клавиатурой
    await bot.send_message(message.from_user.id, service_message, reply_markup=kb_inline)
    await state.clear()


# SECTION ITEM
@dp.message(lambda message: message.text == items_button)
async def send_message_items(message: Message, state: FSMContext):
    cursor = connection.cursor()
    cursor.execute("SELECT name, description FROM item_group WHERE is_active = true AND is_deleted=false")
    items_groups = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for items_group in items_groups:
        kb_builder.button(text=items_group[0])
        avalible_items_group.append(items_group[0])
    kb_builder.button(text=main_menu_button)    
    kb_builder.adjust(3)    
    kb = kb_builder.as_markup(resize_keyboard=True)
    await bot.send_message(message.from_user.id, items_group_message, reply_markup=kb)
    await state.set_state(ChoiseItem.item_group)

@dp.message(ChoiseItem.item_group, F.text.in_(avalible_items_group))
async def send_message_item(message: Message, state: FSMContext):
    await state.update_data(item_group=message.text)
    user_data = await state.get_data()
    cursor = connection.cursor()

    cursor.execute(f"SELECT name FROM item where item_group_name = '{user_data['item_group']}' and is_deleted = false and is_active = true")
    items = cursor.fetchall()
    if not items:
        await bot.send_message(message.from_user.id, items_empty_message)
        return
    kb_builder = ReplyKeyboardBuilder()
    for item in items:
        kb_builder.button(text=item[0])
        avalible_items.append(item[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await bot.send_message(message.from_user.id, items_message, reply_markup=kb)
    await state.set_state(ChoiseItem.item)

@dp.message(ChoiseItem.item, F.text.in_(avalible_items))
async def send_message_item_price(message: Message, state: FSMContext):
    await state.update_data(item=message.text)
    user_data = await state.get_data()

    cursor = connection.cursor()
    cursor.execute(f"SELECT name, description, price, quantity FROM item where item_group_name = '{user_data['item_group']}' and is_deleted = false and is_active = true")
    service = cursor.fetchall()

    price = service[0][2]
    if price % 1 == 0:
        price = int(price)

    service_name = service[0][0]
    service_description = service[0][1].strip().capitalize()

    service_message = (
        f'{'🛍️'} {service_name}:\n\n'
        f'💭 {service_description}\n\n'
        f'📦 Количество: {service[0][3]}\n\n'
        f'💸 Цена: {price} руб.'
    )

    # Создаем Inline-кнопку "Записаться"
    booking_button_inline = InlineKeyboardButton(text="Купить", callback_data="booking")

    # Создаем Inline-клавиатуру с кнопкой "Записаться"
    kb_inline = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[booking_button_inline]])

    # Отправляем сообщение с Inline-клавиатурой
    await bot.send_message(message.from_user.id, service_message, reply_markup=kb_inline)
    await state.clear()

@dp.callback_query()
async def booking_callback_handler(callback_query: CallbackQuery):
    await bot.answer_callback_query(
        callback_query_id=callback_query.id,
        text="Записываем..",
        show_alert=True
    )

@dp.message(lambda message: message.text == "/buy")
async def buy_process(message: Message):
    await bot.send_invoice(message.chat.id,
        title=item_title,
        description=item_description,
        provider_token=os.getenv("TELEGRAM_PAYMENT_TOKEN"),
        need_shipping_address=True,
        currency="RUB",
        is_flexible=True,
        prices=PRICES,
        start_parameter="example",
        payload="test-invoice-payload")
    
@dp.pre_checkout_query(lambda q: True)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(lambda message: message.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    await message.answer(f"Платеж на сумму `{message.successful_payment.total_amount} {message.successful_payment.currency}` совершен успешно!")

@dp.message(lambda message: message.text == main_menu_button)
async def send_message_back(message: Message):
    await message.answer(text=main_menu_message, reply_markup=start_kb)