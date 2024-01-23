from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import settings

#### Инлайн кнопки     ###
tehpodderjka = InlineKeyboardMarkup(row_width=1)
tehpodderjka.add(InlineKeyboardButton('Тех. поддержка', url='https://t.me/Festeval_Pisyunov'))
tehpodderjka.add(InlineKeyboardButton(text="Пополнить баланс",callback_data="pay"))

partnerss = InlineKeyboardMarkup()
partnerss.add(InlineKeyboardButton('Заказать рекламу', url='https://t.me/Festeval_Pisyunov'))
partnerss.add(InlineKeyboardButton('Канал', url='https://t.me/animeboutique'))

chatik = InlineKeyboardMarkup()
chatik.add(InlineKeyboardButton('Наш чат', url='https://t.me/gamer_zoneee'))
# Подписка на канал
channel_subskriber = InlineKeyboardMarkup(row_width=1)
link =InlineKeyboardButton(text="⛓ Ссылка на канал",url=f"https://t.me/{settings.link_channel}")
check_user_group = InlineKeyboardButton(text="✅ Я подписался",callback_data="check_user_group")
channel_subskriber.add(link,check_user_group)
# Админ-меню
admin_menu = InlineKeyboardMarkup()
mail_bt = InlineKeyboardButton(text = '✉️ Рассылка', callback_data = 'mail')
give_uban_bt = InlineKeyboardButton(text = '🚷 Выдать бан/разбан', callback_data = 'uban')
change_balance_bt = InlineKeyboardButton(text = '💳 Изменить баланс', callback_data = 'chb')
admin_menu.add(mail_bt)
admin_menu.add(give_uban_bt, change_balance_bt)
# Кнопка отмены
cancel_menu = InlineKeyboardMarkup()
cancel_bt = InlineKeyboardButton(text = '🔚 Отмена', callback_data = 'cancel')
cancel_menu.add(cancel_bt)
#### Клавиатура      ###
main_menu = ReplyKeyboardMarkup(resize_keyboard = True)
main_menu.add('✔️ Подписаться на канал', '➕ Получить подписчиков')
main_menu.add('👤 Профиль', '🔘 Партнерка')
