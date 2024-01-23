from settings import *
from functions import *
import settings

START = f'🙋‍♂ Добро пожаловать в бот NaokoCoin. Я создан для того, чтобы помогать тебе получать взаимных подписчиков на твой канал. Перед началом использования бота, обязательно прочитай небольшую [инструкцию по использованию бота, а также правила]({LINK_TO_INTRODUCTION_AND_RULES})\n Так же обращаю ваше внимание на то что тут есть один огромный баг, подробнее в правилах!!!'
UPDATE = '🔙 Возвращаемся в главное меню'
LITTLE_SUBCOIN_1 = f'❗️Для раскрутки вашего канала у вас должно быть минимум {LITTLE_SUBCOIN_TO_GET_SUBS} NaokoCoin!'
LITTLE_SUBCOIN_2 = '😳 Недостаточно NaokoCoin!'
SEND_YOUR_CHANNEL = '❕Для получения подписчиков в ваш канал:\n__1) Добавьте в него этого бота\n2) Отправьте сюда юзернейм вашего канала.__'

def SEND_SUB_COUNT_1(m):
    send_sub_count  = f'😀 Хорошо. Теперь отправьте нужное вам количество подписчиков.\n*Доступно:* {user_balance(m.from_user.id)}'
    return send_sub_count
    
def NEW_REFERAL(argument):
    new_referal = f'🥳 Поздравляем, у вас новый реферал!\nВсего рефералов: {referals(argument)}'
    return new_referal
    
def PROFILE(m):
    profile = f'*👤 Имя:* {m.from_user.first_name}\n*📟 ID:* `{m.from_user.id}`\n*💰 Баланс:* {user_balance(m.from_user.id)} *NaokoCoin 🤩*'
    return profile
    
GIVE_CHANNEL_LINK = '''❕*Для начала продвижения:*\n1) Добавьте этого бота в свой канал (должен быть публичным).\n2) Пришлите сюда юзернейм этого канала. Например:\n@babochkiii'''  
CANCEL_TEXT = '🎳 Отменено'
BOT_NOT_IN_CHANNEL = '''❗️❗️❗️Вы не добавили бота в администраторы этого канала. Сначала добавьте бота в нужный вам канал, а уже потом пришлите его юзернейм❗️❗️❗️\n\n*После добавления бота в канал, пришлите сюда юзернейм этого канала!*'''
THIS_IS_NOT_CHANNEL = '''😡 *Это не канал!*\nПришлите сюда юзернейм канала, который вы хотите продвигать!''' 
THIS_IS_NOT_TEXT = '''🤔 *Это не юзернейм канала!*\n\nПришлите сюда юзернейм канала который вы хотите продвигать.'''

def CONFIRM_ADDING_CHANNEL(username, subcount, price):
    confirm_adding_channel = f'''Подтвердите добавление канала для продвижения:\n\n📻 Канал: @{username}\n\n📲 Количество подписчиков: {subcount}\n\n💳 Цена: {price} NaokoCoin''' 
    return confirm_adding_channel
    
CHANNEL_ON_PROMOTION = "❗️Канал уже отправлен на продвижение!"
CHANNEL_ON_PROMOTION_2 = '❌ Такой канал уже на продвижении! Дождитесь пока оно окончится, а потом попробуйте ещё раз.\nДобавьте другой канал или отмените действие:'
CHANNEL_SUCCESSFULLY_ADED = '👍 Канал успешно добавлен на продвижение.'
SUBSCRIBE_ON_THIS_CHANNEL = '''Подпишитесь на этот канал:\n1️⃣ Перейдите на канал 👇, подпишитесь ✔️ и пролистайте ленту вверх 🔝👁 (5-10 постов).\n2️⃣ Возвращайтесь⚡️сюда, чтобы получить вознаграждение.'''
NO_HAVE_CHANNELS_FOR_SUBSCRIBE = f"😔 Пока нет каналов для подписки либо вы уже подписались на все каналы. Дождитесь появления в списке новых каналов или закажите пиар своего канала❕"

def CHANNEL_WAS_DEL_FROM_CHANNEL(id, link_to_rules):
    message =f'❗️Вам экстренное сообщение.\n\nБыло обнаружено, что бот был удален из вашего канала (ID канала: `{id}`)\n😡 В качестве штрафа за нарушение [правил]({link_to_rules}), продвижение канала остановлено и только половина из неиспользованных для продвижения этого канала NaokoCoin, возвращены вам на баланс.\nПроверка юзеров на отписку также остановлена.'
    return message
    
def SUBSCRIBE_IS_SUCCESSFULLY(username):
    message = f'👍 Вы успешно подписались на канал: @{username}\nВам на баланс начислено 1 NaokoCoin 💠.'
    return message
    
def YOU_ARE_LATE_FOR_SUBS(username):
    message = f'☹️ Вы не успели подписаться на канал, прежде чем его продвижение окончилось.\nМожете отписаться от этого канала: @{username}'
    return message
    
YOU_DONT_COMPLETE_SUBS = '😡 Вы ещё не подписались на этот канал!'
    
def PARTNERS(username_of_bot, user_id, ref_count):
    message = f'❕*Приглашайте в бота друзей и знакомых* по своей реферальной ссылке и получайте по *2 NaokoCoin* за каждого.\n*👣 Количество рефералов:* {ref_count}\n*🧲 Ваша реферальная ссылка:* \nhttps://t.me/{settings.botname}?start={user_id}'
    return message
    
SELECT_ADMIN_MENU_BUTTON = '🛠 Выберите пункт меню:'
SEND_MESSAGE_FOR_SEND = '🖋 Отправьте _текст/фото/видео/gif/файл_ для рассылки.'

def MAILING_END(all, die):
    alive = all - die
    message = f'✅ Рассылка окончена.\n\n🤠 Успешно доставлено сообщений: {alive}\n\n😢 Недоставлено сообщений: {die}'
    return message
    
SEND_USER_FOR_UBAN = '❓Для бана отправьте:\n\nID 0\n\n❓Для разбана отправьте:\n\nID 1'
NOT_INTEGER = 'Одно из передаваемых значений не число!'
LITTLE_VALUE = '😡 Вы должны были отправить два значения разделяя их пробелом!'
YOU_WAS_BANNED = '🥳 Поздравляю! Вас забанили в этом боте. Теперь вы не сможете им пользоваться.'
YOU_WAS_HACK_ME = '🤭 Вы меня взломали! Что мне теперь делать?'
SEND_USER_FOR_CHANGE_BALANCE = '''❗️Для изменения баланса человека отправьте:\n\nID значение'''

def SUBSCRIPTION_VIOLATION(username, sub_term, count_of_fine):
    message = f'😡 Вы отписались от канала @{username} раньше чем через {sub_term} дней!\n\nВ качестве штрафа с вашего баланса снято {count_of_fine} NaokoCoin 💠.'
    return message
    
YOU_DID_THIS = '🙂 Самый хитрый?\nТы ведь уже выполнял это задание)'
    


