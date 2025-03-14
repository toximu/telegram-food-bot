from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
import databasehandler
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json

API_TOKEN = '2069344034:AAG6sEMU_7Gui5eUs68apXk2ovHvcwdrehw'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
admin_chat_id = -759769788

f = open('menu.json', encoding='UTF-8')
f = json.load(f)

class StatesGroupinfo(StatesGroup):
	input_name = State()
	input_time = State()
	input_adress = State()
	check_up = State()
con = sqlite3.connect('db.db')
cur = con.cursor()



cur.execute("DROP TABLE IF EXISTS dishes")
cur.execute('CREATE TABLE IF NOT EXISTS dishes(dish TEXT PRIMARY KEY, type, price)')
con.commit()
for type in f.keys():
	for dish in f[type]:
		cur.execute('INSERT INTO dishes VALUES (?,?,?)',(dish['name'], type, dish['price']))
		con.commit()


ikb_cart = InlineKeyboardMarkup()
ib_clear = InlineKeyboardButton('Очистить корзину', callback_data = 'clear_cart')
ib_confirm = InlineKeyboardButton('Оформить заказ', callback_data = 'do_order')
ikb_cart.add(ib_clear).add(ib_confirm)


kb_main = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, is_persistent=True)
b_menu = KeyboardButton('Меню')
b_cart = KeyboardButton('Корзина')
kb_main.add(b_menu).add(b_cart)


ikb_list = InlineKeyboardMarkup()

ikb_dict = {}

for i in f.keys():
	ikb_list.add(InlineKeyboardButton(text = i, callback_data=i))
	ikb_dict[i] = InlineKeyboardMarkup()
	for dish in f[i]:
		ikb_dict[i].add(InlineKeyboardButton(text = dish['name']+' '+ str(dish['price'])+' руб.', callback_data=i+'_'+dish['name']))




ikb_check = InlineKeyboardMarkup()
ib_send = InlineKeyboardButton('Отправить', callback_data='send')
ib_cancel = InlineKeyboardButton('Отменить', callback_data='cancel')
ikb_check.add(ib_send).add(ib_cancel)

	


@dp.message_handler(commands=['start'])
async def send_info(message: types.Message):
	await message.answer(text = 'Ты можешь заказать еды', reply_markup=kb_main)

@dp.message_handler(state = StatesGroupinfo.input_name)
async def get_name(message : types.Message, state : FSMContext ):
	await state.update_data(name = message.text)
	await message.answer('Теперь введите время, к которому доставить заказ.')
	await state.set_state(StatesGroupinfo.input_time.state)

@dp.message_handler(state = StatesGroupinfo.input_time)
async def get_time(message : types.Message, state : FSMContext ):
	await state.update_data(time = message.text)
	await message.answer('Пожалуйста назовите адрес.')
	await state.set_state(StatesGroupinfo.input_adress.state)

@dp.message_handler(state = StatesGroupinfo.input_adress)
async def get_adress(message : types.Message, state : FSMContext ):
	await state.update_data(adress = message.text)
	await state.update_data(chatid = message.from_user.id)
	await message.answer('Отлично! Данные зафиксированы!')
	global info
	info = (await state.get_data())
	await message.answer('Перед отправкой проверьте все данные:')
	global order_message
	order_message = f'''
	
	Имя: {info['name']}
	Время доставки: {info['time']}
	Адрес: {info['adress']}
	
	- Корзина -\n\n{databasehandler.get_cart(message.from_user.username)}'''
	await message.answer('- Ваш заказ -'+order_message, reply_markup=ikb_check)
	await state.finish()


	
@dp.callback_query_handler(text = ['send', 'cancel'])
async def send_or_cancel(callback: types.CallbackQuery):
	if callback.data == 'send':
		await bot.send_message(admin_chat_id, '- Новый заказ -'+order_message)
		databasehandler.clear_cart(callback.from_user.username)
	else:
		info.clear()
		await callback.message.answer('Вы отменили заказ!', reply_markup=kb_main)
	await callback.answer()

@dp.message_handler()
async def send_list(message: types.Message):
	if message.text == 'Меню':
		await message.answer(text = 'Выберите раздел:', reply_markup=ikb_list)
	elif message.text == 'Корзина':
		cart = databasehandler.get_cart(message.from_user.username)
		if 'Ваша корзина пуста!' != cart:
			await message.answer(text = '- Ваша корзина -\n\n'+cart, reply_markup=ikb_cart)
		else:
			await message.answer(text = cart)

@dp.callback_query_handler(text = f.keys())
async def get_type(callback: types.CallbackQuery):
	await callback.message.answer('Что вы хотите заказать?', reply_markup=ikb_dict[callback.data])
	await callback.answer()

@dp.callback_query_handler(text = 'clear_cart')
async def get_dish(callback: types.CallbackQuery):
	databasehandler.clear_cart(callback.from_user.username)
	await callback.answer('Корзина очищена!')

@dp.callback_query_handler(text = 'do_order')
async def do_order(callback: types.CallbackQuery, state : FSMContext):
	await callback.message.answer('Как вас зовут?')
	await state.set_state(StatesGroupinfo.input_name.state)
	await callback.answer()


@dp.callback_query_handler()
async def get_dish(callback: types.CallbackQuery):
	databasehandler.create_user_cart(callback.from_user.username)
	dish_type, dish_name = callback.data.split('_')[0], callback.data.split('_')[1]
	databasehandler.add_to_cart(callback.from_user.username, dish_name, dish_type)
	await callback.answer('Товар добавлен в корзину!')


executor.start_polling(dp)