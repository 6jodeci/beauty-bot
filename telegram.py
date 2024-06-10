import os
import mysql_db
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
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

avalible_hall = [
    "Мужской зал",
    "Женский зал",
    "Общий зал"
]

avalible_services = []


class RegisterUser(StatesGroup):
    full_name = State()
    email = State()
    phone_number = State()

class ChoiseService(StatesGroup):
    service_group = State()
    hall = State()
    service = State()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext):
    # Проверяем, зарегистрирован ли пользователь в базе данных
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE id = %s", (message.from_user.id,))
    user = cursor.fetchone()

    # Если пользователь зарегистрирован, отправляем ему сообщение с помощью
    if user:
        await message.answer(help_message, reply_markup=start_kb)
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
        print(f"INSERT: {cursor.rowcount} rows inserted")
        await message.answer(registration_success)
        await message.answer(help_message)
    except Exception as e:
        print(f"INSERT error: {e}")
        connection.rollback()
        await message.answer(registration_error)

    cursor.close()
    await state.clear()

@dp.message(lambda message: message.text == "Где мы находимся?")
async def send_location(message: Message):
    await bot.send_location(message.chat.id,
                            longitude=location_longitude,
                            latitude=location_latitude)
    await bot.send_message(message.chat.id, location)

@dp.message(lambda message: message.text == "Услуги")
async def send_message_services(message: Message, state: FSMContext):
    cursor = connection.cursor()
    cursor.execute("SELECT name, description FROM service_group WHERE is_active = true AND is_deleted=false")
    service_groups = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for service_group in service_groups:
        kb_builder.button(text=service_group[0])
        avalible_services_group.append(service_group[0])
    kb_builder.button(text="На главную")    
    kb_builder.adjust(3)    
    kb = kb_builder.as_markup(resize_keyboard=True)
    await bot.send_message(message.from_user.id, 'Выберите тип услуги', reply_markup=kb)
    await state.set_state(ChoiseService.service_group)

@dp.message(ChoiseService.service_group, F.text.in_(avalible_services_group))
async def send_message_hall(message: Message, state: FSMContext):
    await state.update_data(service_group=message.text)
    await bot.send_message(message.from_user.id, 'Выберите зал', reply_markup=hall_kb)
    await state.set_state(ChoiseService.hall)

@dp.message(ChoiseService.hall, F.text.in_(avalible_hall))
async def send_message_service(message: Message, state: FSMContext):
    await state.update_data(hall=message.text)
    user_data = await state.get_data()
    cursor = connection.cursor()
    if user_data['hall'] == 'Мужской зал':
        cursor.execute(f"SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'male' and is_deleted = false and is_active = true and service_group_name = '{user_data['service_group']}'",)
    elif user_data['hall'] == 'Женский зал':
        cursor.execute(f"SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'female' and is_deleted = false and is_active = true and service_group_name = '{user_data['service_group']}'")
    elif user_data['hall'] == 'Общий зал':
        cursor.execute(f"SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'all' and is_deleted = false and is_active = true and service_group_name = '{user_data['service_group']}'")
    services = cursor.fetchall()
    if not services:
        await bot.send_message(message.from_user.id, 'Нет доступных услуг')
        return
    kb_builder = ReplyKeyboardBuilder()
    for service_group in services:
        kb_builder.button(text=service_group[0])
        avalible_services.append(service_group[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text="На главную"))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await bot.send_message(message.from_user.id, 'Выберите услугу', reply_markup=kb)
    await state.set_state(ChoiseService.service)

@dp.message(ChoiseService.service, F.text.in_(avalible_services))
async def send_message_service(message: Message, state: FSMContext):
    await state.update_data(service=message.text)
    user_data = await state.get_data()
    cursor = connection.cursor()
    cursor.execute(f"SELECT name, description, price from service WHERE name = '{user_data['service']}'")
    service = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.button(text="Записаться")
    kb_builder.row(KeyboardButton(text="На главную"))

    kb = kb_builder.as_markup(resize_keyboard=True)

    await bot.send_message(message.from_user.id, 'Услуга: ' + service[0][0] + '\nОписание: ' + service[0][1] + '\nЦена: ' + str(service[0][2]) + ' руб.', reply_markup=kb)
    await state.set_state(ChoiseService.service)






























# @dp.message(lambda message: message.text == "Женский зал")
# async def send_message_female_hall(message: Message):
#     await message.answer("Я перешел в женский зал")
#     cursor = connection.cursor()
#     cursor.execute("SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'female' and is_deleted = false and is_active = true")
#     female_services = cursor.fetchall()
#     kb_builder = ReplyKeyboardBuilder()
#     for service_group in female_services:
#         kb_builder.button(text=service_group[0])
#     kb_builder.adjust(3)
#     kb = kb_builder.as_markup(resize_keyboard=True)
#     await bot.send_message(message.from_user.id, 'Выберите тип услуги', reply_markup=kb)

# @dp.message(lambda message: message.text == "Общий зал")
# async def send_message_common_hall(message: Message):
#     await message.answer("Я перешел в общий зал")
#     cursor = connection.cursor()
#     cursor.execute("SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'all' and is_deleted = false and is_active = true")
#     all_services = cursor.fetchall()
#     kb_builder = ReplyKeyboardBuilder()
#     for service_group in all_services:
#         kb_builder.button(text=service_group[0])
#     kb_builder.adjust(3)
#     kb = kb_builder.as_markup(resize_keyboard=True)
#     await bot.send_message(message.from_user.id, 'Выберите тип услуги', reply_markup=kb)

# @dp.message(lambda message: message.text == "Мужской зал")
# async def send_message_male_hall(message: Message):
#     await message.answer("Я перешел в мужский зал")
#     cursor = connection.cursor()
#     cursor.execute("SELECT name, description, service_group_name, price, gender FROM service WHERE gender = 'male' and is_deleted = false and is_active = true")
#     male_services = cursor.fetchall()
#     kb_builder = ReplyKeyboardBuilder()
#     for service_group in male_services:
#         kb_builder.button(text=service_group[0])
#     kb_builder.adjust(3)
#     kb = kb_builder.as_markup(resize_keyboard=True)
#     await bot.send_message(message.from_user.id, 'Выберите тип услуги', reply_markup=kb)

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

@dp.message(lambda message: message.text == "На главную")
async def send_message_back(message: Message):
    await message.answer("Я вернулся в главное меню", reply_markup=start_kb)