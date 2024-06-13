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
from admin_keyboard import *
from const import *
import random
import asyncio
import string
from datetime import datetime, timedelta

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

class CreateServiceGroup(StatesGroup):
    name = State()
    description = State()
    choise_hall = State()
    active = State()

class CreateItemGroup(StatesGroup):
    name = State()
    description = State()
    active = State()


class CreateService(StatesGroup):
    name = State()
    description = State()
    group = State()
    price = State()
    hall = State()
    active = State()

class CreateItem(StatesGroup):
    name = State()
    description = State()
    price = State()
    quantity = State()
    group = State()
    active = State()

class DeleteItemGroup(StatesGroup):
    name = State()

class DeleteItem(StatesGroup):
    name = State()

class DeleteServiceGroup(StatesGroup):
    name = State()

class DeleteService(StatesGroup):
    name = State()

class Booking(StatesGroup):
    date = State()
    time = State()
    initial = State()

class UpdateItem(StatesGroup):
    name = State()
    description = State()
    price = State()
    quantity = State()
    group = State()
    active = State()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext):
    # Проверяем, зарегистрирован ли пользователь в базе данных
    cursor = connection.cursor()
    cursor.execute("SELECT is_admin, id FROM user WHERE id = %s", (message.from_user.id,))
    user = cursor.fetchone()

    if user and user[0] == True:  # Если пользователь является админом
        await message.answer(admin_start_message, reply_markup=admin_kb)
        return

    elif user:  # Если пользователь зарегистрирован, но не является админом
        await message.answer(start_message, reply_markup=start_kb)

    else:  # Если пользователь не зарегистрирован
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
        await message.answer(registration_success, reply_markup=start_kb)
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
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.button(text=main_menu_button)
    kb = kb_builder.as_markup(resize_keyboard=True)

    await message.answer(help_message, reply_markup=kb)
    await state.set_state(Support.help_message)
    
@dp.message(Support.help_message)
async def send_help_message(message: Message, state: FSMContext):
    if message.text == main_menu_button:
        await bot.send_message(message.chat.id, main_menu_message, reply_markup=start_kb)
        await state.clear()
        return
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
    await state.update_data(service_name=service_name)


def create_date_list():
    date_list = []
    today = datetime.today()
    for i in range(7):
        date = today + timedelta(days=i)
        date_list.append(date.strftime("%d.%m.%Y"))
    return date_list

def create_time_list():
    time_list = []
    for i in range(10, 18):
        time_list.append(f'{i:02d}:00')
    return time_list

@dp.callback_query(F.data == 'booking')
async def booking(callback: CallbackQuery, state: FSMContext):

    date_list = create_date_list()
    kb_builder = ReplyKeyboardBuilder()
    for date in date_list:
        kb_builder.button(text=date)
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await bot.send_message(callback.from_user.id, choise_data_message, reply_markup=kb)
    await callback.answer()
    await state.set_state(Booking.date)

@dp.message(Booking.date, F.text.in_(create_date_list()))
async def send_message_time(message: Message, state: FSMContext):
    await state.update_data(date=message.text)

    time_list = create_time_list()

    kb_builder = ReplyKeyboardBuilder()
    for time in time_list:
        kb_builder.button(text=time)
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)

    await bot.send_message(message.from_user.id, choise_time_message, reply_markup=kb)
    await state.set_state(Booking.time)

@dp.message(Booking.time)
async def confirm_booking(message: Message, state: FSMContext):
    if message.text not in create_time_list():
        await bot.send_message(message.from_user.id, 'Некорректное время. Пожалуйста, выберите время из предложенного списка.')
        state.clear()
        return

    data = await state.get_data()
    service_name = data.get('service_name')
    selected_date = data.get('date')
    selected_time = message.text
    selected_datetime = datetime.strptime(f'{selected_date} {selected_time}', '%d.%m.%Y %H:%M')

    cursor = connection.cursor()
    cursor.execute(f"SELECT id FROM user WHERE is_admin = true ORDER BY RAND() LIMIT 1")
    admin_id = cursor.fetchone()[0]

    username = "@" + message.from_user.username
    await bot.send_message(admin_id, f'Пользователь {username} записался на {selected_date} в {selected_time}.\nУслуга {service_name}.')

    await bot.send_message(message.from_user.id, f'Вы выбрали запись на {selected_date} в {selected_time}.\nУслуга {service_name}.', reply_markup=start_kb)
    
    cursor.execute(f"INSERT INTO booking (username, service_name, time) VALUES (%s, %s, %s)", (username, service_name, selected_datetime))
    connection.commit()

    reminder_time = selected_datetime - timedelta(hours=1)
    if reminder_time > datetime.now():
        await asyncio.sleep((reminder_time - datetime.now()).total_seconds())
        await bot.send_message(message.from_user.id, f'Напоминаем, что у вас сегодня запись на {selected_time}.\nУслуга {service_name}.')

    await state.clear()

@dp.message(lambda message: message.text == user_booking_button)
async def get_bookings_for_the_next_7_days(message: Message):
    current_datetime = datetime.now()

    end_datetime = current_datetime + timedelta(days=7)

    query = f"""
        SELECT username, service_name, time
        FROM booking
        WHERE time >= %s AND time < %s
    """

    cursor = connection.cursor()
    cursor.execute(query, (current_datetime, end_datetime))
    bookings = cursor.fetchall()

    bookings_string = booking_seven_days_message + '\n\n'
    for booking in bookings:
        bookings_string += f'Пользователь: {booking[0]}\nУслуга: {booking[1]}\nВремя: {booking[2]}\n\n\n'

    await bot.send_message(message.from_user.id, bookings_string)

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
    item = cursor.fetchall()

    price = item[0][2]
    if price % 1 == 0:
        price = int(price)

    item_name = item[0][0]
    item_description = item[0][1].strip().capitalize()

    item_message = (
        f'{'🛍️'} {item_name}:\n\n'
        f'💭 {item_description}\n\n'
        f'📦 Остаток: {item[0][3]}\n\n'
        f'💸 Цена: {price} руб.'
    )

    # Создаем Inline-кнопку "Записаться"
    booking_button_inline = InlineKeyboardButton(text="Купить", callback_data="buy")

    # Создаем Inline-клавиатуру с кнопкой "Записаться"
    kb_inline = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[booking_button_inline]])

    # Отправляем сообщение с Inline-клавиатурой
    await bot.send_message(message.from_user.id, item_message, reply_markup=kb_inline)
    
    # передать item_message в state
    await state.update_data(item_name=item_name, item_description=item_description, price=price)

@dp.callback_query(lambda c: c.data == "buy")
async def process_callback_booking(callback_query: CallbackQuery, state: FSMContext):
    item_data = await state.get_data()  
    item_name = item_data['item_name']
    item_description = item_data['item_description']
    price = item_data['price']
    await bot.answer_callback_query(callback_query.id)
    await bot.send_invoice(
        chat_id=callback_query.message.chat.id,
        title=item_name,
        description=item_description,
        provider_token=os.getenv("TELEGRAM_PAYMENT_TOKEN"),
        currency="RUB",
        prices=[types.LabeledPrice(label=item_name, amount=price * 100)],
        start_parameter="purchase",
        payload="purchase"
    )
    
@dp.pre_checkout_query(lambda q: True)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(lambda message: message.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, state: FSMContext):
    item_data = await state.get_data()
    item_name = item_data['item_name']

    # Уменьшаем количество на 1
    cursor = connection.cursor()
    try:
        cursor.execute(f"UPDATE item SET quantity = quantity - 1 WHERE name = '{item_name}'")
    except Exception as e:
        print(e)

    connection.commit()

    # Генерируем номер заказа
    order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Отправляем пользователю сообщение с номером заказа и рандомным числом
    await message.answer(
        f"Платеж на сумму `{message.successful_payment.total_amount / 100} {message.successful_payment.currency}` совершен успешно!\n\n"
        f"Товар: {item_name}\n"
        f"Количество: 1\n"
        f"Ваш номер заказа: {order_number}\n"
    )


    cursor = connection.cursor()
    cursor.execute(f"SELECT id FROM user WHERE is_admin = true ORDER BY RAND() LIMIT 1")
    admin_id = cursor.fetchone()[0]
    # Отправляем админу сообщение о новом заказе
    await bot.send_message(
        admin_id,
        f"Новый заказ!\n\n"
        f"Пользователь: @{message.from_user.username} (ID: {message.from_user.id})\n"
        f"Товар: {item_name}\n"
        f"Количество: 1\n"
        f"Сумма: {message.successful_payment.total_amount / 100} {message.successful_payment.currency}\n"
        f"Номер заказа: {order_number}\n"
    )
@dp.message(lambda message: message.text == main_menu_button)
async def send_message_back(message: Message):
    cursor = connection.cursor()
    cursor.execute("SELECT is_admin FROM user WHERE id = %s", (message.from_user.id,))
    user = cursor.fetchone()

    if user[0] == True:
        await message.answer(main_menu_message, reply_markup=admin_kb)
        return
    else:
        await message.answer(text=main_menu_message, reply_markup=start_kb)


@dp.message(lambda message: message.text == create_service_group_button)
async def create_service_group(message: Message, state: FSMContext):
    await message.answer(text=create_service_group_message, reply_markup=edit_kb)



@dp.message(lambda message: message.text == create_item_group_button)
async def create_item_group(message: Message, state: FSMContext):
    await message.answer(text=create_item_group_message, reply_markup=edit_kb)

@dp.message(lambda message: message.text == delete_button)
async def delete_item(message: Message, state: FSMContext):
    await state.set_state(DeleteItem.name)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM item")
    items = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for item in items:
        kb_builder.button(text=item[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(text=delete_item_message, reply_markup=kb)

@dp.message(DeleteItem.name)
async def delete_item_name(message: Message, state: FSMContext):
    selected_item = message.text
    cursor = connection.cursor()
    cursor.execute(f"UPDATE item SET is_deleted = 1, is_active = 0 WHERE name = '{selected_item}'")
    connection.commit()
    await message.answer(f"Товар '{selected_item}' был помечен как удаленный.")
    await state.clear()

@dp.message(lambda message: message.text == edit_button)
async def update_item(message: Message, state: FSMContext):
    await state.set_state(UpdateItem.name)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM item")
    items = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for item in items:
        kb_builder.button(text=item[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(text=update_item_message, reply_markup=kb)

@dp.message(UpdateItem.name)
async def update_item_name(message: Message, state: FSMContext):
    selected_item = message.text
    await state.update_data(name=selected_item)
    await message.answer(text=update_item_message)
    await state.set_state(UpdateItem.description)

@dp.message(UpdateItem.description)
async def update_item_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(text=update_item_description_message)
    await state.set_state(UpdateItem.price)

@dp.message(UpdateItem.price)
async def update_item_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer(text=update_new_item_quantity_message)
    await state.set_state(UpdateItem.quantity)

@dp.message(UpdateItem.quantity)
async def update_item_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.answer(text=update_item_group_message)
    await state.set_state(UpdateItem.group)

@dp.message(UpdateItem.group)
async def update_item_active(message: Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer(text=update_new_item_active_message)
    await state.set_state(UpdateItem.active)

@dp.message(UpdateItem.active)
async def update_item_active(message: Message, state: FSMContext):
    await state.update_data(active=message.text)
    item_data = await state.get_data()
    cursor = connection.cursor()
    if item_data['active'] == 'Да':
        item_data['active'] = 1
    else:
        item_data['active'] = 0
    print(f'{item_data["name"]}, {item_data["description"]}, {item_data["active"]}, {item_data["group"]}, {item_data["quantity"]}, {item_data["price"]}')
    try:
        cursor.execute("UPDATE item SET name = %s, description = %s, quantity = %s, item_group_name = %s, price = %s, is_active = %s WHERE name = %s", (item_data['name'], item_data['description'], item_data['quantity'], item_data['group'], item_data['price'], item_data['active'], item_data['name']))
    except Exception as e:
        print(e)
    connection.commit()
    await message.answer(f"Товар '{item_data['name']}' был обновлен.")
    await state.clear()

@dp.message(lambda message: message.text == create_item_button)
async def create_item(message: Message, state: FSMContext):
    await state.set_state(CreateItem.name)
    await message.answer(text=create_item_message, reply_markup=edit_kb)

@dp.message(lambda message: message.text == create_button)
async def create_item(message: Message, state: FSMContext):
    await state.set_state(CreateItem.name)
    await message.answer(text=create_new_item_message)

@dp.message(CreateItem.name)
async def create_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text=create_new_item_description_message)
    await state.set_state(CreateItem.description)

@dp.message(CreateItem.description)
async def create_item_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(text=update_item_price_message)
    await state.set_state(CreateItem.price)

@dp.message(CreateItem.price)
async def create_item_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer(text=create_new_item_quantity_message)
    await state.set_state(CreateItem.quantity)

@dp.message(CreateItem.quantity)
async def create_item_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.answer(text=create_new_item_group_message)
    await state.set_state(CreateItem.group)

@dp.message(CreateItem.group)
async def create_item_active(message: Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer(text=create_new_item_active_message)
    await state.set_state(CreateItem.active)

@dp.message(CreateItem.active)
async def create_item_active(message: Message, state: FSMContext):
    await state.update_data(active=message.text)
    item_data = await state.get_data()
    cursor = connection.cursor()
    if item_data['active'] == 'Да':
        item_data['active'] = 1
    else:
        item_data['active'] = 0
    print(f'{item_data["name"]}, {item_data["description"]}, {item_data["active"]}, {item_data["group"]}, {item_data["quantity"]}, {item_data["price"]}')
    try:
        cursor.execute(f"INSERT INTO item (name, description, quantity, item_group_name, price, is_active) VALUES ('{item_data['name']}', '{item_data['description']}', '{item_data['quantity']}', '{item_data['group']}', '{item_data['price']}', '{item_data['active']}');")
    except Exception as e:
        print(e)
    connection.commit()
    await message.answer(f"Товар '{item_data['name']}' был создан.")
    await state.clear()

@dp.message(lambda message: message.text == create_service_button)
async def create_service(message: Message, state: FSMContext):
    await state.set_state(CreateService.name)
    await message.answer(text=create_service_message, reply_markup=edit_kb)

@dp.message(lambda message: message.text == delete_button)
async def delete_service(message: Message, state: FSMContext):
    await state.set_state(DeleteService.name)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM service")
    services = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for service in services:
        kb_builder.button(text=service[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(text=delete_service_message, reply_markup=kb)

@dp.message(DeleteService.name)
async def delete_service_name(message: Message, state: FSMContext):
    selected_service = message.text
    cursor = connection.cursor()
    cursor.execute(f"UPDATE service SET is_deleted = 1, is_active = 0 WHERE name = '{selected_service}'")
    connection.commit()
    await message.answer(f"Сервис '{selected_service}' был помечен как удаленный.")
    await state.clear()

@dp.message(lambda message: message.text == create_button)
async def create_service(message: Message, state: FSMContext):
    await state.set_state(CreateService.name)
    await message.answer(text=create_new_service_message)

@dp.message(CreateService.name)
async def create_service_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text=create_new_service_description_message)
    await state.set_state(CreateService.description)

@dp.message(CreateService.description)
async def create_service_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(text=create_new_service_group_message)
    await state.set_state(CreateService.group)

@dp.message(CreateService.group)
async def create_service_group(message: Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer(text=create_new_serivce_price_message)
    await state.set_state(CreateService.price)

@dp.message(CreateService.price)
async def create_service_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer(text=create_new_service_choise_hall_message)
    await state.set_state(CreateService.hall)

@dp.message(CreateService.hall)
async def create_service_hall(message: Message, state: FSMContext):
    await state.update_data(hall=message.text)
    await message.answer(text=create_new_serivce_active_message)
    await state.set_state(CreateService.active)

@dp.message(CreateService.active)
async def create_service_active(message: Message, state: FSMContext):
    await state.update_data(active=message.text)
    service_data = await state.get_data()
    cursor = connection.cursor()
    if service_data['active'] == 'Да':
        service_data['active'] = 1
    else:
        service_data['active'] = 0
    print(f'{service_data["name"]}, {service_data["description"]}, {service_data["active"]}, {service_data["group"]}, {service_data["price"]}, {service_data["hall"]}')
    try:
        cursor.execute("INSERT INTO service (name, description, service_group_name, price, is_active, gender) VALUES (%s, %s, %s, %s, %s, %s)", (service_data['name'], service_data['description'], service_data['group'], service_data['price'], service_data['active'], service_data['hall']))
    except Exception as e:
        print(e) 
    connection.commit()
    await message.answer(f"Услуга '{service_data['name']}' была создана.")
    state.clear()

@dp.message(lambda message: message.text == delete_button)
async def delete_service_group(message: Message, state: FSMContext):
    await state.set_state(DeleteItem.name)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM service_group")
    service_groups = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for service_group in service_groups:
        kb_builder.button(text=service_group[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(text=delete_service_group_message, reply_markup=kb)

@dp.message(DeleteServiceGroup.name)
async def delete_service_group_name(message: Message, state: FSMContext):
    selected_service_group = message.text
    cursor = connection.cursor()
    cursor.execute(f"UPDATE service_group SET is_deleted = 1, is_active = 0 WHERE name = '{selected_service_group}'")
    connection.commit()
    await message.answer(f"Группа услуг '{selected_service_group}' была помечена как удаленная.")
    await state.clear()

@dp.message(lambda message: message.text == delete_button)
async def delete_item_group(message: Message, state: FSMContext):
    await state.set_state(DeleteItem.name)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM item_group")
    item_groups = cursor.fetchall()
    kb_builder = ReplyKeyboardBuilder()
    for item_group in item_groups:
        kb_builder.button(text=item_group[0])
    kb_builder.adjust(3)
    kb_builder.row(KeyboardButton(text=main_menu_button))
    kb = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(text=delete_item_group_message, reply_markup=kb)

@dp.message(DeleteServiceGroup.name)
async def delete_item_group_name(message: Message, state: FSMContext):
    selected_item_group = message.text
    cursor = connection.cursor()
    cursor.execute(f"UPDATE item_group SET is_deleted = 1, is_active = 0 WHERE name = '{selected_item_group}'")
    connection.commit()
    await message.answer(f"Группа услуг '{selected_item_group}' была помечена как удаленная.")
    await state.clear()