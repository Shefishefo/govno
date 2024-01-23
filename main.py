from settings import *
from messages import *
from functions import *
import time
import random
import sqlite3
import keyboards
import json
import requests
from aiogram import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.exceptions import BotBlocked
import asyncio
from aiogram.utils.exceptions import Unauthorized
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.filters import Command, Text
from datetime import datetime,timedelta

loop = asyncio.get_event_loop()

bot = Bot(token = token, loop = loop)
dp = Dispatcher(bot, storage = MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

class UserStates(Helper):
    GET_CHANNEL_TO_UP = ListItem()
    GET_SUB_COUNT = ListItem()
    CONFIRMATION = ListItem()
    GET_MSG_FOR_MAIL = ListItem()
    GET_USER_FOR_UBAN = ListItem()
    GET_USER_FOR_CHB = ListItem()

async def user_in_channel_checker():
    last_check = get_last_check()
    if last_check == None and count_of_channels() >= 1:
        global check_user_in_ch
        async def check_user_in_ch():
            channels = get_channels_for_check()
            for x in channels:
                my_id = await bot.get_me()
                try:
                    status_bot_in_channel = await bot.get_chat_member(chat_id = x[1], user_id = my_id.id)
                    status_bot_in_channel = status_bot_in_channel.status
                except (Unauthorized, BotBlocked):
                    status_bot_in_channel = 'left'
                if status_bot_in_channel == 'administrator':
                    subs = x[2]
                    checked_users = eval(x[-1])
                    for user in subs:
                        if user not in checked_users:
                            get_user = await bot.get_chat_member(chat_id = x[1], user_id = user)
                            time_from_subs = x[2][user]
                            if get_user.status == 'left' and ((time_from_subs - datetime.datetime.now()).days < SUBSCRIPTION_TERM) and user_was_fine(x[0], user) == False:
                                add_user_to_fined(x[0], user)
                                change_balance(user, FINE_FOR_UNSUBSCRIBING)
                                increase_fine_count(user)
                                username = await bot.get_chat(chat_id = x[1])
                                await bot.send_message(user, SUBSCRIPTION_VIOLATION(username.username, SUBSCRIPTION_TERM, FINE_FOR_UNSUBSCRIBING))
                            elif get_user.status == 'left' and ((time_from_subs - datetime.datetime.now()).days >= SUBSCRIPTION_TERM) and user_was_fine(x[0], user) == False:
                                add_member_to_checked(x[0], user)
                else:
                    writer = edit_promotion_status(x[0], 0)
                    id = x[1]
                    add_promotion_to_uncheck(x[0])
                    await bot.send_message(writer, CHANNEL_WAS_DEL_FROM_CHANNEL(id, LINK_TO_INTRODUCTION_AND_RULES), parse_mode = 'Markdown')
            set_last_check()
        await check_user_in_ch()
    elif last_check != None and count_of_channels >= 1:
        now_time = datetime.datetime.now()
        delta = last_check - now_time
        if delta.seconds >= 3600:
            await check_user_in_ch()
    
@dp.message_handler(lambda m: user_banned(m.from_user.id) == False, commands = ['start'])
async def start_commands_handle(m: types.Message):
    if is_user_in_db(m.from_user.id) < 1:
        argument = m.get_args()
        if (argument is not None) and (argument.isdigit() == True) and (is_user_in_db(argument)) == 1:
            add_user_to_db(m.from_user.id, ref_father = argument)
            await m.reply(START, reply = False, parse_mode = 'Markdown', reply_markup = keyboards.main_menu)
            await bot.send_message(text = NEW_REFERAL(argument), chat_id = argument)
        else:
            add_user_to_db(m.from_user.id)
            await m.reply(START, reply = False, parse_mode = 'Markdown', reply_markup = keyboards.main_menu)
    else:
        await m.reply(UPDATE, reply = False, parse_mode = 'Markdown', reply_markup = keyboards.main_menu)
    
@dp.message_handler(lambda m: m.from_user.id in admins, commands = ['admin'])
async def admin_command_handle(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
		await m.reply(SELECT_ADMIN_MENU_BUTTON, reply = False, reply_markup = keyboards.admin_menu)
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    

    
@dp.message_handler(lambda m: m.text == '👤 Профиль' and user_banned(m.from_user.id) == False)
async def profile_button_handle(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
		await m.reply(PROFILE(m), reply = False, parse_mode = 'Markdown', reply_markup=keyboards.tehpodderjka)
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.message_handler(lambda m: m.text == '➕ Получить подписчиков' and user_banned(m.from_user.id) == False)
async def add_channel_handle(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    if user_balance(m.from_user.id) >= LITTLE_SUBCOIN_TO_GET_SUBS:
	        state = dp.current_state(user = m.from_user.id)
	        await state.set_state('GET_CHANNEL_TO_UP')
	        await m.reply(GIVE_CHANNEL_LINK, reply = False, parse_mode = 'Markdown', reply_markup = keyboards.cancel_menu)
	    else:
	        await m.reply(LITTLE_SUBCOIN_1, reply = False)
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.message_handler(state = 'GET_CHANNEL_TO_UP')
async def channel_to_up_handle(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    try:
	        if m.content_type == 'text':
	            my_id = await bot.get_me()
	            get_channel= await bot.get_chat(m.text)
	            if get_channel.type == 'channel':
	                status_bot_in_channel = await bot.get_chat_member(chat_id = m.text, user_id = my_id.id)
	                if check_channel_in_db(get_channel.id) == 1:
	                    if status_bot_in_channel.status == 'administrator':
	                        number = save_channel(channel_id = get_channel.id, writer = m.from_user.id)
	                        cancel_promotion = InlineKeyboardMarkup()
	                        cancel_promotion.add(InlineKeyboardButton(text = '🔚 Отмена', callback_data = 'cancel_' + str(number)))
	                        await bot.delete_message(message_id = m.message_id  - 1, chat_id = m.from_user.id)
	                        await m.reply(SEND_SUB_COUNT_1(m), reply = False, parse_mode = 'Markdown', reply_markup = cancel_promotion)
	                        state = dp.current_state(user = m.from_user.id)
	                        await state.set_state('GET_SUB_COUNT')
	                    else:
	                        await bot.delete_message(message_id = m.message_id  - 1, chat_id = m.from_user.id)
	                        await m.reply(BOT_NOT_IN_CHANNEL, parse_mode = 'Markdown', reply_markup = keyboards.cancel_menu)
	                elif check_channel_in_db(get_channel.id) == 0:
	                    await m.reply(CHANNEL_ON_PROMOTION_2, reply = False, reply_markup = keyboards.cancel_menu)
	            else:
	                await bot.delete_message(message_id = m.message_id  - 1, chat_id = m.from_user.id)
	                await m.reply(THIS_IS_NOT_CHANNEL, parse_mode = 'Markdown', reply_markup = keyboards.cancel_menu)
	        else:
	            await m.reply(THIS_IS_NOT_TEXT, parse_mode = 'Markdown', reply_markup = keyboards.cancel_menu)
	    except Exception as e:
	        await m.reply(e, reply_markup = keyboards.cancel_menu)
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)

@dp.callback_query_handler(text="pay")
async def pay(call: types.CallbackQuery):
    wait_minutes_pay = 15
    dtn = datetime.now() + timedelta(minutes=wait_minutes_pay)
    comment = random.randint(100000, 999999)
    dtn = dtn.strftime("%m-%d %H:%M:%S")
    btn = await create_link(comment)
    await bot.send_message(call.from_user.id,f"Прошу прощения но пока что киви не работает, обращайтесь к админу @Festeval_Pisyunov*",reply_markup=btn,parse_mode="Markdown") 

async def create_link(comment):
	wait_minutes_pay = 15
	dtn = datetime.now() + timedelta(minutes=wait_minutes_pay)
	dtn = dtn.strftime("%Y-%m-%d %H%M")
	dtn = dtn.replace(" ", "T") # создается дата на 15 минут больше, типо сколько счет будет держаться, минуты можно указать в конфиге
	link = f'https://oplata.qiwi.com/create?publicKey={settings.p2p_qiwi_public_key}&comment={comment}&billId={comment}&customFields[themeCode]=YVAN-PPcftOY-G-&lifetime={dtn}'
	check_link = requests.get(link)
	btn1 = InlineKeyboardButton(text="⛓ Ссылка на оплату",url=link)
	btn2 = InlineKeyboardButton(text=" 👌 Я оплатил",callback_data=f"checks,{comment}")
	btn = InlineKeyboardMarkup(row_width=1).add(btn1,btn2)
	return btn

@dp.callback_query_handler(Text(startswith="checks"))
async def end(call: types.CallbackQuery):
	comment = call.data.split(",")[1]
	all_head = {"Authorization": f"Bearer {settings.p2p_qiwi_secret_key}", "Accept": "application/json"}
	req = requests.get(f'https://api.qiwi.com/partner/bill/v1/bills/{comment}', headers=all_head).json()
	check = await check_status(req)
	if check:
		balances = req["amount"]["value"]
		balance = int(float(balances))
		replace(id=call.from_user.id,amount=balance)
		await call.message.edit_text(text=f"*Вы успешно пополнили баланс на сумму {balances}*", parse_mode="Markdown")
		
		for admin in settings.admins:
			await bot.send_message(admin,f"Пользователь @{call.from_user.username} успешно пополнил счет на {balances}₽", parse_mode="Markdown")
	else:
		await bot.send_message(call.from_user.id,"Не оплачено!")

async def check_status(req):
	try:
		if req['status']['value'] == 'PAID':
			return True
		else:
			return False
	except:
		return False

@dp.message_handler(state = 'GET_SUB_COUNT')
async def handle_get_sub_count(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    if (m.content_type == 'text') and (m.text.isdigit() == True) and (int(m.text) >= LITTLE_SUBCOIN_TO_GET_SUBS) and user_balance(m.from_user.id) >= int(m.text):
	        save_channel(subs_count = int(m.text), writer = m.from_user.id)
	        channel_stat = get_channel_stat(m.from_user.id)
	        username = await bot.get_chat(channel_stat[0][0][1])
	        username = username.username
	        confirmation_menu = InlineKeyboardMarkup()
	        confirmation_menu.add(InlineKeyboardButton(text = '🔚 Отмена', callback_data = 'cancel_' + str(channel_stat[-1])), InlineKeyboardButton(text = '✅ Подтвердить', callback_data = 'confirm_' + str(channel_stat[-1])))
	        state = dp.current_state(user = m.from_user.id)
	        await state.set_state('CONFIRMATION')
	        await bot.delete_message(message_id = m.message_id  - 1, chat_id = m.from_user.id)
	        await m.reply(CONFIRM_ADDING_CHANNEL(username, channel_stat[0][0][0], channel_stat[0][0][0]), reply = False, reply_markup = confirmation_menu)
	    else:
	        channel_stat = get_channel_stat(m.from_user.id)
	        username = await bot.get_chat(channel_stat[0][0][1])
	        username = username.username
	        cancel_wnum_menu= InlineKeyboardMarkup()
	        cancel_wnum_menu.add(InlineKeyboardButton(text = '🔚 Отмена', callback_data = 'cancel_' + str(channel_stat[-1])))
	        await m.reply(LITTLE_SUBCOIN_2, reply = False, reply_markup = cancel_wnum_menu)
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.message_handler(lambda m: m.text == '✔️ Подписаться на канал' and user_banned(m.from_user.id) == True)
async def sent_instruction_for_subscribe(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    black_list = []
	    while True:
	        channels_list = channel_for_subscribe(m.from_user.id)
	        if channels_list != 0 and len(channels_list) > len(black_list):
	            channel_to_subscribe = random.choice(list(channels_list))
	            if channel_to_subscribe not in black_list:
	                my_id = await bot.get_me()
	                try:
	                    bot_status = await bot.get_chat_member(chat_id = channel_to_subscribe, user_id = my_id.id)
	                    bot_status = bot_status.status
	                except (Unauthorized, BotBlocked):
	                    bot_status = 'left'
	                if bot_status == "administrator":
	                    status_of_user = await bot.get_chat_member(chat_id = channel_to_subscribe, user_id = m.from_user.id)
	                    if status_of_user.status == 'left':
	                        username = await bot.get_chat(chat_id = channel_to_subscribe)
	                        subscribe_menu = InlineKeyboardMarkup()
	                        subscribe_menu.add(InlineKeyboardButton(text = 'Перейти к каналу', url = 'tg://resolve?domain=' + username.username))
	                        subscribe_menu.add(InlineKeyboardButton(text = 'Проверить подписку', callback_data = 'sub_' + str(channels_list[channel_to_subscribe])))
	                        await m.reply(SUBSCRIBE_ON_THIS_CHANNEL, reply_markup = subscribe_menu, reply = False)
	                        break
	                    else:
	                        black_list.append(channel_to_subscribe)
	                else:
	                    writer = edit_promotion_status(channels_list[channel_to_subscribe], 0)
	                    id = channel_to_subscribe
	                    await bot.send_message(writer, CHANNEL_WAS_DEL_FROM_CHANNEL(id, LINK_TO_INTRODUCTION_AND_RULES))
	        else:
	            await m.reply(NO_HAVE_CHANNELS_FOR_SUBSCRIBE, reply_markup=keyboards.chatik, reply = False)
	            break
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.message_handler(content_types = ['text', 'video', 'photo', 'document', 'animation'], state = 'GET_MSG_FOR_MAIL')
async def send_mail(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    state = dp.current_state(user = m.from_user.id)
	    await state.reset_state()
	    users = get_users_for_mailing()
	    if m.content_type == 'text':
	        all_users = 0
	        blocked_users = 0
	        for x in users:
	            try:
	                await bot.send_message(x[0], m.html_text, parse_mode = 'HTML')
	                all_users += 1
	                await asyncio.sleep(0.3)
	            except BotBlocked:
	                blocked_users += 1
	        await m.reply(MAILING_END(all_users, blocked_users), reply = False)
	    if m.content_type == 'photo':
	        all_users = 0
	        blocked_users = 0
	        for x in users:
	            try:
	                await bot.send_photo(x[0], photo = m.photo[-1].file_id, caption = m.html_text, parse_mode = 'HTML')
	                all_users += 1
	                await asyncio.sleep(0.3)
	            except BotBlocked:
	                blocked_users += 1
	        await m.reply(MAILING_END(all_users, blocked_users), reply = False)
	    if m.content_type == 'video':
	        all_users = 0
	        blocked_users = 0
	        for x in users:
	            try:
	                await bot.send_video(x[0], video = m.video.file_id, caption = m.html_text, parse_mode = 'HTML')
	                all_users += 1
	                await asyncio.sleep(0.3)
	            except BotBlocked:
	                blocked_users += 1
	        await m.reply(MAILING_END(all_users, blocked_users), reply = False)
	    if m.content_type == 'animation':
	        all_users = 0
	        blocked_users = 0
	        for x in users:
	            try:
	                await bot.send_animation(x[0], animation = m.animation.file_id)
	                all_users += 1
	                await asyncio.sleep(0.3)
	            except BotBlocked:
	                blocked_users += 1
	        await m.reply(MAILING_END(all_users, blocked_users), reply = False)
	    if m.content_type == 'document':
	        all_users = 0
	        blocked_users = 0
	        for x in users:
	            try:
	                await bot.send_document(x[0], document = m.document.file_id)
	                all_users += 1
	                await asyncio.sleep(0.3)
	            except BotBlocked:
	                blocked_users += 1
	        await m.reply(MAILING_END(all_users, blocked_users), reply = False)
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.message_handler(lambda m: m.text == '🔘 Партнерка' and user_banned(m.from_user.id) == False)
async def referal_button_handle(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    get_bot = await bot.get_me()
	    await m.reply(PARTNERS(get_bot.username, m.from_user.id, referals(m.from_user.id)), disable_web_page_preview = True, parse_mode = 'Markdown', reply_markup=keyboards.partnerss, reply = False)
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.callback_query_handler(lambda c: c.data == 'cancel', state = UserStates.all())
async def cancel_button_handle(c: types.callback_query):
	user_status = await bot.get_chat_member(channel_id,c.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    state = dp.current_state(user = c.from_user.id)
	    await state.reset_state()
	    await c.message.edit_text(CANCEL_TEXT)
	else:
		await bot.send_message(c.from_user.id,"✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)

@dp.message_handler(lambda m: m.from_user.id in admins, content_types = ['text'], state = 'GET_USER_FOR_CHB')
async def handle_user_for_chb(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    list = m.text.split(' ')
	    if len(list) == 2:
	        id = list[0]
	        value = list[1]
	        if id.isdigit() and value.lstrip('-').isdigit():
	            result = change_balance(id, value)
	            await m.reply(result, reply = False)
	        else:
	            await m.reply(NOT_INTEGER, reply = False)
	    else:
	        await m.reply(LITTLE_VALUE, reply = False)
	    state = dp.current_state(user = m.from_user.id)
	    await state.reset_state()
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.message_handler(lambda m: m.from_user.id in admins, content_types = ['text'], state = 'GET_USER_FOR_UBAN')
async def handle_user_for_uban(m: types.Message):
	user_status = await bot.get_chat_member(channel_id,m.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    list = m.text.split(' ')
	    if len(list) == 2:
	        id = list[0]
	        decision = list[1]
	        if id.isdigit() and decision.isdigit():
	            result = uban_user(id, decision)
	            await m.reply(result, reply = False)
	            if int(decision) == 0:
	                await bot.send_message(id, YOU_WAS_BANNED)
	        else:
	            await m.reply(NOT_INTEGER, reply = False)
	    else:
	        await m.reply(LITTLE_VALUE, reply = False)
	    state = dp.current_state(user = m.from_user.id)
	    await state.reset_state()
	else:
		await m.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.callback_query_handler(lambda c: 'cancel_' in c.data, state = ['CONFIRMATION', 'GET_SUB_COUNT'])
async def cancel_wnum_button_handler(c: types.callback_query):
	user_status = await bot.get_chat_member(channel_id,c.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    number = c.data.replace('cancel_', '')
	    status = delete_channel_from_db(number)
	    if status == 0:
	        await c.message.edit_text(CHANNEL_ON_PROMOTION)
	        state = dp.current_state(user = c.from_user.id)
	        await state.reset_state()
	    else:
	        await c.message.edit_text(CANCEL_TEXT)
	        state = dp.current_state(user = c.from_user.id)
	        await state.reset_state()
	else:
		await bot.send_message(c.from_user.id,"✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.callback_query_handler(lambda c: 'confirm_' in c.data, state = 'CONFIRMATION')
async def confirm_button_handler(c :types.callback_query):
	user_status = await bot.get_chat_member(channel_id,c.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    number = c.data.replace('confirm_', '')
	    luck = confirm_order(number)
	    if luck == 1:
	        await c.message.edit_text(CHANNEL_SUCCESSFULLY_ADED)
	        state = dp.current_state(user = c.from_user.id)
	        await state.reset_state()
	    else:
	        await c.message.edit_text(luck)
	        state = dp.current_state(user = c.from_user.id)
	        await state.reset_state()
	else:
		await bot.send_message(c.from_user.id,"✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.callback_query_handler(lambda c: 'sub_' in c.data)
async def check_user_in_channel(c: types.CallbackQuery):
	user_status = await bot.get_chat_member(channel_id,c.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    number = c.data.replace('sub_', '')
	    info = promotion_info(number)
	    if check_user_to_do_this(number, info[1]) == False:
	        if info[0] == 1:
	            my_id = await bot.get_me()
	            try:
	                bot_status = await bot.get_chat_member(chat_id = info[1], user_id = my_id.id)
	                bot_status = bot_status.status
	            except (Unauthorized, BotBlocked):
	                bot_status = 'left'
	            if bot_status == "administrator":
	                status_of_user = await bot.get_chat_member(chat_id = info[1], user_id = c.from_user.id)
	                if status_of_user.status != 'left':
	                    add_to_subs = add_user_to_subscribers(number, c.from_user.id)
	                    username = await bot.get_chat(chat_id = add_to_subs[1])
	                    if add_to_subs[0] == 1:
	                        await c.message.edit_text(SUBSCRIBE_IS_SUCCESSFULLY(username.username))
	                    else:
	                        await c.message.edit_text(YOU_ARE_LATE_FOR_SUBS(username.username))
	                else:
	                    await c.answer(text = YOU_DONT_COMPLETE_SUBS, show_alert = True)
	            else:
	                writer = edit_promotion_status(number, 0)
	                add_promotion_to_uncheck(number)
	                await bot.send_message(writer, CHANNEL_WAS_DEL_FROM_CHANNEL(add_to_subs[1], LINK_TO_INTRODUCTION_AND_RULES))
	        else:
	            await c.message.edit_text(YOU_ARE_LATE_FOR_SUBS(username.username))
	    else:
	        await c.message.edit_text(YOU_DID_THIS)
	else:
		await bot.send_message(c.from_user.id,"✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.callback_query_handler(lambda c: c.data == 'mail')
async def handle_mail_button(c: types.CallbackQuery):
	user_status = await bot.get_chat_member(channel_id,c.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    await c.message.edit_text(SEND_MESSAGE_FOR_SEND, parse_mode = 'Markdown', reply_markup = keyboards.cancel_menu)
	    state = dp.current_state(user = c.from_user.id)
	    await state.set_state('GET_MSG_FOR_MAIL')
	else:
		await bot.send_message(c.from_user.id,"✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.callback_query_handler(lambda c: c.data == 'uban')
async def handle_uban_button(c: types.CallbackQuery):
	user_status = await bot.get_chat_member(channel_id,c.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    await c.message.edit_text(SEND_USER_FOR_UBAN, reply_markup = keyboards.cancel_menu)
	    state = dp.current_state(user = c.from_user.id)
	    await state.set_state('GET_USER_FOR_UBAN')
	else:
		await bot.send_message(c.from_user.id,"✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
@dp.callback_query_handler(lambda c: c.data == 'chb')
async def handle_chb_button(c: types.CallbackQuery):
	user_status = await bot.get_chat_member(channel_id,c.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    await c.message.edit_text(SEND_USER_FOR_CHANGE_BALANCE)
	    state = dp.current_state(user = c.from_user.id)
	    await state.set_state('GET_USER_FOR_CHB')
	else:
		await bot.send_message(c.from_user.id,"✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)
    
async def on_shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    
@dp.message_handler(content_types=["text"])
async def alll(message: types.Message):
	user_status = await bot.get_chat_member(channel_id,message.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
	    user_status = await bot.get_chat_member(channel_id,message.from_user.id)
	    if user_status.status == "member" or user_status.status == "administrator" or user_status.status == "creator":
	        await message.answer("🔙 Возвращаемся в главное меню")
	    else:
	        await message.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ", reply_markup=keyboards.channel_subskriber)
	else:
		await message.answer("✉️ Для продолжения пользования ботом, пожалуйста, подпишитесь на наш канал.\nПубликуем ᴄᴛиᴋᴇᴩы & ᴀᴩᴛы & ᴀʙы ",reply_markup=keyboards.channel_subskriber)

@dp.callback_query_handler(text="check_user_group")
async def ppp(call: types.CallbackQuery):
	user_status = await bot.get_chat_member(channel_id,call.from_user.id)
	if user_status.status == "creator" or user_status.status =="administrator" or user_status.status == "member":
		await bot.send_message(call.from_user.id,"Дальше пользуйтесь кнопками",reply_markup=keyboards.main_menu)
	else:
		await bot.send_message(call.from_user.id,"😔 Вы ещё не подписались на наш канал. Не забудьте нажать на кнопку выше, если вы уже сделали это")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True, on_shutdown = on_shutdown, loop = loop)
