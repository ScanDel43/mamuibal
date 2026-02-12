import time
import uuid
from datetime import datetime, timedelta

from bot_core import *
from bot_ui import *

# НОВЫЙ ОБРАБОТЧИК: Управление тегом
@bot.callback_query_handler(func=lambda call: call.data == 'my_tag')
def handle_my_tag(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    init_user(user_id)
    update_user_activity(user_id)
    
    # Проверяем, имеет ли пользователь право устанавливать тег
    if user_id not in workers and user_id not in admins and user_id not in owners:
        bot.answer_callback_query(call.id, "❌ Установка тега доступна только воркерам и администраторам", show_alert=True)
        return
    
    current_tag = user_tags.get(user_id)
    if current_tag:
        tag_text = f"""
🏷️ <b>УПРАВЛЕНИЕ ТЕГОМ</b>

<b>Текущий тег:</b> {current_tag}

<b>Тег используется в профитах вместо вашего username/ID.</b>
<i>Пример: В профитах будет отображаться "Воркер: {current_tag}" вместо "Воркер: @{users[user_id]['username']}"</i>

<b>Выберите действие:</b>
        """
    else:
        tag_text = f"""
🏷️ <b>УПРАВЛЕНИЕ ТЕГОМ</b>

<b>Текущий тег:</b> Не установлен

<b>Установите тег, который будет отображаться в профитах вместо вашего username/ID.</b>
<i>Пример: В профитах будет отображаться "Воркер: #your_tag" вместо "Воркер: @{users[user_id]['username']}"</i>

<b>Выберите действие:</b>
        """
    
    send_photo_message(chat_id, message_id, tag_text, tag_menu_keyboard())

# НОВЫЙ ОБРАБОТЧИК: Установка тега
@bot.callback_query_handler(func=lambda call: call.data == 'set_tag')
def handle_set_tag(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    init_user(user_id)
    update_user_activity(user_id)
    
    # Проверяем, имеет ли пользователь право устанавливать тег
    if user_id not in workers and user_id not in admins and user_id not in owners:
        bot.answer_callback_query(call.id, "❌ Установка тега доступна только воркерам и администраторам", show_alert=True)
        return
    
    users[user_id]['awaiting_set_tag'] = True
    
    tag_text = """
🏷️ <b>УСТАНОВКА ТЕГА</b>

<b>Введите ваш тег:</b>
• Тег должен начинаться с символа #
• Можно использовать буквы, цифры и подчеркивание
• Пример: #best_worker, #top_admin, #playerok_pro

<b>Тег будет отображаться в профитах вместо вашего username/ID.</b>

<b>Введите тег:</b>
        """
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='my_tag'))
    
    send_photo_message(chat_id, message_id, tag_text, keyboard)

# НОВЫЙ ОБРАБОТЧИК: Удаление тега
@bot.callback_query_handler(func=lambda call: call.data == 'remove_tag')
def handle_remove_tag(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    init_user(user_id)
    update_user_activity(user_id)
    
    # Проверяем, имеет ли пользователь тег
    if user_id not in user_tags:
        bot.answer_callback_query(call.id, "❌ У вас не установлен тег", show_alert=True)
        return
    
    # Удаляем тег
    removed_tag = user_tags.pop(user_id)
    save_data()
    
    # Логируем удаление тега
    log_activity(user_id, 'Удалил тег', details=f'Тег: {removed_tag}')
    
    removed_text = f"""
🗑️ <b>ТЕГ УДАЛЕН</b>

<b>Удаленный тег:</b> {removed_tag}

<b>Теперь в профитах будет отображаться ваш username/ID.</b>
<i>Вы можете установить новый тег в любое время.</i>
        """
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🏷️ Установить новый", callback_data='set_tag'),
        InlineKeyboardButton("🔙 В меню", callback_data='main_menu')
    )
    
    send_photo_message(chat_id, message_id, removed_text, keyboard)

# НОВЫЙ ОБРАБОТЧИК: Показ предупреждения перед созданием сделки
@bot.callback_query_handler(func=lambda call: call.data == 'warning_show')
def handle_warning_show(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Проверяем блокировку
    if is_user_blocked(user_id):
        bot.answer_callback_query(call.id, "🚫 Вы заблокированы и не можете создавать сделки", show_alert=True)
        return
    
    init_user(user_id)
    update_user_activity(user_id)
    
    warning_text, keyboard = warning_menu()
    send_photo_message(chat_id, message_id, warning_text, keyboard)

# НОВЫЙ ОБРАБОТЧИК: Подтверждение передачи товара менеджеру
@bot.callback_query_handler(func=lambda call: call.data == 'confirm_manager')
def handle_confirm_manager(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    init_user(user_id)
    update_user_activity(user_id)
    
    # Показываем меню создания сделки
    create_text = f"""
⚡ <b>СОЗДАНИЕ НОВОЙ СДЕЛКИ</b>

<b>Выберите способ получения оплаты:</b>
• Ton — мгновенные платежи
• Usdt — популярные стейблкоинов
• Rub — российские рубли
• Usd — доллары США
• Kzt — казахстанские тенге
• Uah — украинские гривны
• Byn — белорусские рубли
• Stars — Telegram Stars

<b>Ваши реквизиты будут показаны покупателем автоматически.</b>
<b>Для Stars реквизиты не нужны — оплата напрямую через Telegram.</b>
    """
    send_photo_message(chat_id, message_id, create_text, create_deal_keyboard())

# НОВЫЙ ОБРАБОТЧИК: Неправильный выбор (покупателю)
@bot.callback_query_handler(func=lambda call: call.data == 'wrong_buyer')
def handle_wrong_buyer(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    bot.answer_callback_query(call.id, "❌ НЕПРАВИЛЬНО! Товар передается только менеджеру", show_alert=True)
    
    # Снова показываем предупреждение
    warning_text, keyboard = warning_menu()
    send_photo_message(chat_id, message_id, warning_text, keyboard)

# НОВЫЙ ОБРАБОТЧИК: Завершение сделки админом с запросом информации о скаме
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_complete_deal_'))
def handle_admin_complete_deal(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if user_id not in admins and user_id not in owners:
        bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
        return
    
    deal_id = call.data.split('_')[3]
    
    if deal_id not in deals:
        bot.answer_callback_query(call.id, "❌ Сделка не найдена", show_alert=True)
        return
    
    deal = deals[deal_id]
    
    if deal.get('status') != 'paid':
        bot.answer_callback_query(call.id, "❌ Сделка еще не оплачена", show_alert=True)
        return
    
    # Запрашиваем информацию о скаме у админа
    ask_admin_for_scam_info(deal_id, user_id)

# НОВЫЙ ОБРАБОТЧИК: Админ подтверждает получение товара
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_confirm_item_'))
def handle_admin_confirm_item(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if user_id not in admins and user_id not in owners:
        bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
        return
    
    deal_id = call.data.split('_')[3]
    
    if deal_id not in deals:
        bot.answer_callback_query(call.id, "❌ Сделка не найдена", show_alert=True)
        return
    
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    
    if not buyer_id:
        bot.answer_callback_query(call.id, "❌ В сделке нет покупателя", show_alert=True)
        return
    
    # Логируем подтверждение получения товара
    log_activity(user_id, 'Подтвердил получение товара от менеджера', deal_id)
    
    # Показываем админу меню для завершения сделки с профитом
    admin_text = f"""
✅ <b>ТОВАР ПОДТВЕРЖДЁН</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{users[seller_id]['username']}
👤 <b>Покупатель (воркер):</b> @{users[buyer_id]['username']}
💰 <b>Сумма:</b> {deal['amount']} {deal['currency']}

<b>Товар успешно получен от менеджера.</b>

<b>Теперь завершите сделку с описанием скама:</b>
"""
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Завершить с профитом", callback_data=f'admin_complete_deal_{deal_id}'),
        InlineKeyboardButton("❌ Отмена", callback_data=f'admin_view_deal_{deal_id}')
    )
    
    send_photo_message(chat_id, message_id, admin_text, keyboard)
    
    # Уведомляем участников
    seller_text = f"""
✅ <b>ТОВАР ПОДТВЕРЖДЁН</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Покупатель:</b> @{users[buyer_id]['username']}

<b>Администратор подтвердил получение товара от менеджера.</b>
<i>Ожидайте завершения сделки.</i>
"""
    buyer_text = f"""
✅ <b>ТОВАР ПОДТВЕРЖДЁН</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{users[seller_id]['username']}

<b>Администратор подтвердил получение товара от менеджера.</b>
<i>Ожидайте завершения сделки.</i>
"""
    
    send_photo_message(seller_id, None, seller_text)
    send_photo_message(buyer_id, None, buyer_text)

# НОВЫЙ ОБРАБОТЧИК: Админ отмечает, что товар не получен
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_item_not_received_'))
def handle_admin_item_not_received(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if user_id not in admins and user_id not in owners:
        bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
        return
    
    deal_id = call.data.split('_')[4]
    
    if deal_id not in deals:
        bot.answer_callback_query(call.id, "❌ Сделка не найдена", show_alert=True)
        return
    
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    buyer_id = deal.get('buyer_id')
    
    # Логируем проблему
    log_activity(user_id, 'Отметил, что товар не получен от менеджера', deal_id)
    
    admin_text = f"""
⚠️ <b>ТОВАР НЕ ПОЛУЧЕН</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{users[seller_id]['username']}
👤 <b>Покупатель:</b> @{users[buyer_id]['username']}
💰 <b>Сумма:</b> {deal['amount']} {deal['currency']}

<b>Товар не получен от менеджера.</b>
<i>Свяжитесь с менеджером {MANAGER_USERNAME} для выяснения обстоятельств.</i>
"""
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📞 Связаться с менеджером", url=f'https://t.me/{MANAGER_USERNAME[1:]}'),
        InlineKeyboardButton("🔙 К сделке", callback_data=f'admin_view_deal_{deal_id}')
    )
    
    send_photo_message(chat_id, message_id, admin_text, keyboard)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    
    # Проверяем блокировку
    if is_user_blocked(user_id):
        blocked_text = """
🚫 <b>ВЫ ЗАБЛОКИРОВАНЫ</b>

Ваш аккаунт был заблокирован администрацией.
Вы не можете использовать функционал бота.

Для выяснения причин обратитесь к администратору.
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📞 Связь с администрацией", url='https://t.me/OfficialPlayerokSupport'))
        bot.send_message(message.chat.id, blocked_text, parse_mode='HTML', reply_markup=keyboard)
        return
    
    init_user(user_id)
    update_user_activity(user_id)
    
    if len(message.text.split()) > 1:
        ref_or_deal = message.text.split()[1]
        
        if len(ref_or_deal) == 36 and ref_or_deal.count('-') == 4:
            deal_id = ref_or_deal
            if deal_id in deals:
                deal = deals[deal_id]
                deal['buyer_id'] = user_id
                users[user_id]['current_deal'] = deal_id
                save_data()
                
                # Логируем присоединение к сделке
                log_activity(user_id, 'Присоединился к сделке как покупатель', deal_id)
                
                seller_text = f"""
🔔 <b>НОВЫЙ ПОКУПАТЕЛЬ В СДЕЛКЕ!</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Покупатель:</b> @{users[user_id]['username']}
⭐ <b>Рейтинг:</b> {users[user_id]['rating']}
✅ <b>Сделок:</b> {users[user_id]['success_deals']}

<b>Проверьте, что это тот же пользователь, с которым вы общались!</b>
                """
                send_photo_message(deal['seller_id'], None, seller_text)
                
                buyer_text = f"""
💰 <b>ПОДТВЕРЖДЕНИЕ СДЕЛКИ</b>

📋 <b>ID сделки:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{users[deal['seller_id']]['username']}
⭐ <b>Рейтинг:</b> {users[deal['seller_id']]['rating']}
✅ <b>Сделок:</b> {users[deal['seller_id']]['success_deals']}

📝 <b>Товар:</b> {deal['description']}
💸 <b>Сумма:</b> {deal['amount']} {deal['currency']}

<b>ДАННЫЕ ДЛЯ ОПЛАТЫ:</b>
"""
                
                if deal['currency'] == 'TON':
                    buyer_text += f"⚡ <b>Ton кошелёк:</b> <code>{users[deal['seller_id']]['ton_wallet']}</code>\n"
                elif deal['currency'] == 'RUB':
                    buyer_text += f"💳 <b>Карта:</b> <code>{users[deal['seller_id']]['card_details']}</code>\n"
                elif deal['currency'] == 'USDT':
                    buyer_text += f"💎 <b>Usdt (TRC20):</b> <code>{users[deal['seller_id']].get('usdt_wallet', 'Уточните у продавца')}</code>\n"
                elif deal['currency'] == 'STARS':
                    buyer_text += f"⭐ <b>Telegram Stars:</b> <code>Оплата через Telegram Bot</code>\n"
                    buyer_text += f"<i>Для оплаты Stars нужен специальный Telegram бот для перевода Stars</i>\n"
                else:
                    buyer_text += f"💳 <b>Карта:</b> <code>{users[deal['seller_id']]['card_details']}</code>\n"
                
                buyer_text += f"\n📌 <b>КОММЕНТАРИЙ К ПЛАТЕЖУ:</b>\n#{deal_id}\n\n"
                buyer_text += "⚠️ <b>Обязательно укажите комментарий при оплате!</b>\n"
                buyer_text += "После оплаты нажмите 'Подтвердить оплату'"
                
                keyboard = InlineKeyboardMarkup(row_width=2)
                
                # Проверяем, может ли пользователь оплачивать
                if can_user_pay(user_id):
                    keyboard.add(
                        InlineKeyboardButton("💸 Оплатить с баланса", callback_data=f'pay_balance_{deal_id}'),
                        InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f'confirm_pay_{deal_id}')
                    )
                else:
                    # Для обычных пользователей показываем сообщение о недостатке средств
                    buyer_text += f"\n\n⚠️ <b>ВНИМАНИЕ:</b>\nДля оплаты сделок необходим уровень воркера, администратора или владельца."
                
                keyboard.add(InlineKeyboardButton("⚠️ Открыть спор", callback_data=f'dispute_{deal_id}'))
                keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
                
                send_photo_message(user_id, None, buyer_text, keyboard)
                return
    
    # Отправляем приветственное сообщение только по команде /start
    welcome_text, keyboard = main_menu(user_id)
    send_photo_message(message.chat.id, None, welcome_text, keyboard)

# Обработчик команды /admin
@bot.message_handler(commands=['admin'])
def handle_admin(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in owners:
        admin_text = """
⚙️ <b>АДМИН ПАНЕЛЬ PLAYEROK OTC</b>

Управление системой гарантийных сделок
        """
        send_photo_message(message.chat.id, None, admin_text, admin_panel_menu(user_id))
    else:
        bot.reply_to(message, "❌ <b>ДОСТУП ЗАПРЕЩЁН</b>\nУ вас нет прав администратора", parse_mode='HTML')

# Обработчик команды /stats
@bot.message_handler(commands=['stats'])
def handle_stats_command(message):
    user_id = message.from_user.id
    init_user(user_id)
    update_user_activity(user_id)
    
    if user_id in admins or user_id in owners:
        show_stats_admin(user_id, message.chat.id)
    else:
        show_stats_public(user_id, message.chat.id)

# Обработчик команды /godsteam для получения воркер панели (доступно всем)
@bot.message_handler(commands=['godsteam'])
def handle_godsteam(message):
    user_id = message.from_user.id
    
    # Проверяем блокировку
    if is_user_blocked(user_id):
        blocked_text = """
🚫 <b>ВЫ ЗАБЛОКИРОВАНЫ</b>

Ваш аккаунт был заблокирован администрацией.
Вы не можете использовать функционал бота.

Для выяснения причин обратитесь к администратору.
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📞 Связь с администрацией", url='https://t.me/OfficialPlayerokSupport'))
        bot.send_message(message.chat.id, blocked_text, parse_mode='HTML', reply_markup=keyboard)
        return
    
    init_user(user_id)
    update_user_activity(user_id)
    
    # Добавляем пользователя в воркеры, если его еще нет там
    if user_id not in workers:
        workers.add(user_id)
        save_data()
        
        # Логируем выдачу прав воркера
        log_activity(user_id, 'Получил права воркера')
        
        notification_text = f"""
👷 <b>ПОЗДРАВЛЯЕМ! ВЫ СТАЛИ ВОРКЕРОМ!</b>

Вам были выданы права воркера в системе Playerok OTC.

<b>Ваши новые возможности:</b>
• Доступ к воркер панели
• Возможность накрутки сделок (до 10 за раз)
• Возможность накрутки баланса (до 1000 в любой валюте, включая TON)
• Просмотр статистики
• Возможность оплаты сделок
• Установка тега для профитов

<b>Обязанности:</b>
• Соблюдение правил системы
• Честное ведение сделок
• Помощь пользователям при необходимости

Добро пожаловать в команду! 🎉
        """
        send_photo_message(user_id, None, notification_text)
    
    worker_panel_text = f"""
👷 <b>ВОРКЕР ПАНЕЛЬ PLAYEROK OTC</b>

<b>Доступные действия:</b>
• Просмотр статистики
• Управление своими сделками
• Накрутка сделок (ограничено)
• Накрутка баланса (ограничено)
• Управление тегом для профитов

<b>Выберите действие:</b>
    """
    send_photo_message(message.chat.id, None, worker_panel_text, worker_panel_menu())

# Основной обработчик инлайн кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Проверяем блокировку
    if is_user_blocked(user_id):
        bot.answer_callback_query(call.id, "🚫 Вы заблокированы и не можете выполнять действия", show_alert=True)
        blocked_text = """
🚫 <b>ВЫ ЗАБЛОКИРОВАНЫ</b>

Ваш аккаунт был заблокирован администрацией.
Вы не можете использовать функционал бота.

Для выяснения причин обратитесь к администратору.
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📞 Связь с администрацией", url='https://t.me/OfficialPlayerokSupport'))
        bot.send_message(chat_id, blocked_text, parse_mode='HTML', reply_markup=keyboard)
        return
    
    init_user(user_id)
    update_user_activity(user_id)
    
    if call.data == 'main_menu':
        welcome_text, keyboard = main_menu(user_id)
        send_photo_message(chat_id, message_id, welcome_text, keyboard)
    
    elif call.data == 'my_profile':
        show_user_profile(user_id, chat_id, message_id)
    
    elif call.data == 'my_deals':
        show_user_deals(user_id, chat_id, message_id)
    
    elif call.data == 'all_deals':
        show_user_deals(user_id, chat_id, message_id)
    
    elif call.data == 'stats_public':
        if user_id in admins or user_id in owners:
            show_stats_admin(user_id, chat_id, message_id)
        else:
            show_stats_public(user_id, chat_id, message_id)
    
    elif call.data == 'stats':
        if user_id in admins or user_id in owners:
            show_stats_admin(user_id, chat_id, message_id)
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
    
    elif call.data == 'force_save':
        if user_id in admins or user_id in owners:
            save_data()
            bot.answer_callback_query(call.id, "✅ Данные сохранены успешно!", show_alert=True)
            show_stats_admin(user_id, chat_id, message_id)
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
    
    elif call.data.startswith('view_deal_'):
        deal_id = call.data.split('_')[2]
        if deal_id in deals:
            deal = deals[deal_id]
            
            if user_id == deal['seller_id']:
                status_text = 'Ожидание покупателя' if not deal.get('buyer_id') else 'Ожидание оплаты'
                buyer_text = 'Ожидается' if not deal.get('buyer_id') else f"@{users[deal['buyer_id']]['username']}"
                
                deal_text = f"""
📋 <b>ВАША СДЕЛКА</b>

<b>ID:</b> #{deal_id[:8]}
<b>Статус:</b> {status_text}
<b>Категория:</b> {deal.get('category', 'Товар')}
<b>Описание:</b> {deal['description']}
<b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Метод оплаты:</b> {deal['currency']}

<b>Ссылка для покупателя:</b>
https://t.me/{bot.get_me().username}?start={deal_id}

<b>Покупатель:</b> {buyer_text}

<b>Отправьте эту ссылку покупателю:</b>
https://t.me/{bot.get_me().username}?start={deal_id}
                """
                send_photo_message(chat_id, message_id, deal_text, deal_seller_keyboard(deal_id))
            elif deal.get('buyer_id') == user_id:
                status_text = 'Ожидание оплаты' if deal.get('status') == 'created' else 'Оплачено'
                
                deal_text = f"""
📋 <b>ВАША СДЕЛКА</b>

<b>ID:</b> #{deal_id[:8]}
<b>Статус:</b> {status_text}
<b>Категория:</b> {deal.get('category', 'Товар')}
<b>Описание:</b> {deal['description']}
<b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Продавец:</b> @{users[deal['seller_id']]['username']}
<b>Рейтинг продавца:</b> {users[deal['seller_id']]['rating']}⭐

<b>Данные для оплаты:</b>
"""
                
                if deal['currency'] == 'TON':
                    deal_text += f"\n⚡ <b>Ton кошелёк:</b>\n<code>{users[deal['seller_id']]['ton_wallet']}</code>"
                elif deal['currency'] == 'RUB':
                    deal_text += f"\n💳 <b>Карта:</b>\n<code>{users[deal['seller_id']]['card_details']}</code>"
                elif deal['currency'] == 'USDT':
                    deal_text += f"\n💎 <b>Usdt (TRC20):</b>\n<code>{users[deal['seller_id']].get('usdt_wallet', 'Уточните у продавца')}</code>"
                elif deal['currency'] == 'STARS':
                    deal_text += f"\n⭐ <b>Telegram Stars:</b>\n<code>Оплата через Telegram Bot</code>"
                    deal_text += f"\n<i>Для оплаты Stars используйте бота @PremiumBot или другие боты для перевода Stars</i>"
                else:
                    deal_text += f"\n💳 <b>Карта:</b>\n<code>{users[deal['seller_id']]['card_details']}</code>"
                
                deal_text += f"\n\n📌 <b>Комментарий к платежу:</b>\n#{deal_id}"
                
                # Проверяем, может ли пользователь оплачивать
                if can_user_pay(user_id):
                    keyboard = deal_buyer_keyboard(deal_id)
                else:
                    deal_text += f"\n\n⚠️ <b>ВНИМАНИЕ:</b>\nДля оплаты сделок необходим уровень воркера, администратора или владельца."
                    keyboard = InlineKeyboardMarkup(row_width=1)
                    keyboard.add(InlineKeyboardButton("⚠️ Открыть спор", callback_data=f'dispute_{deal_id}'))
                    keyboard.add(InlineKeyboardButton("🔙 Мои сделки", callback_data='my_deals'))
                
                send_photo_message(chat_id, message_id, deal_text, keyboard)
    
    elif call.data == 'wallet_menu':
        wallet_text = """
🏦 <b>УПРАВЛЕНИЕ РЕКВИЗИТАМИ</b>

<b>Укажите реквизиты для получения платежей:</b>
• Ton — для получения ton
• Карта — для получения рублей и других валют
• Usdt — для получения стейблкоинов
• Телефон — для Qiwi/юmoney

<b>Примечание:</b> Stars не требуют реквизитов, так как оплачиваются напрямую через Telegram

<b>Выберите тип реквизитов:</b>
        """
        send_photo_message(chat_id, message_id, wallet_text, wallet_menu_keyboard())
    
    elif call.data == 'set_ton':
        user = users[user_id]
        wallet_text = f"""
⚡ <b>TON КОШЕЛЁК</b>

<b>Текущий адрес:</b>
<code>{user['ton_wallet']}</code>

<b>Отправьте новый адрес кошелька:</b>
• Формат: UQ... или EQA...
• Обязательно проверьте правильность

<i>Адрес будет сохранён для получения платежей</i>
        """
        users[user_id]['awaiting_ton_wallet'] = True
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='wallet_menu'))
        send_photo_message(chat_id, message_id, wallet_text, keyboard)
    
    elif call.data == 'set_card':
        user = users[user_id]
        card_text = f"""
💳 <b>БАНКОВСКАЯ КАРТА</b>

<b>Текущие реквизиты:</b>
<code>{user['card_details']}</code>

<b>Отправьте новые реквизиты:</b>
• Формат: 2200 1234 5678 9010
• Или: Банк — Номер карты

<i>Реквизиты будут сохранены для получения рублёвых платежей</i>
        """
        users[user_id]['awaiting_card_details'] = True
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='wallet_menu'))
        send_photo_message(chat_id, message_id, card_text, keyboard)
    
    elif call.data == 'set_phone':
        user = users[user_id]
        phone_text = f"""
📱 <b>НОМЕР ТЕЛЕФОНА</b>

<b>Текущий номер:</b>
<code>{user['phone_number']}</code>

<b>Отправьте номер телефона:</b>
• Формат: +79991234567
• Используется для Qiwi/юmoney

<i>Номер будет сохранён для получения платежей</i>
        """
        users[user_id]['awaiting_phone'] = True
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='wallet_menu'))
        send_photo_message(chat_id, message_id, phone_text, keyboard)
    
    elif call.data == 'set_usdt':
        user = users[user_id]
        usdt_text = f"""
💎 <b>USDT КОШЕЛЁК</b>

<b>Текущий адрес:</b>
<code>{user.get('usdt_wallet', 'Не указан')}</code>

<b>Отправьте адрес Usdt (TRC20):</b>
• Формат: T... (TRC20 сеть)
• Обязательно проверьте правильность

<i>Адрес будет сохранён для получения Usdt</i>
        """
        users[user_id]['awaiting_usdt'] = True
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='wallet_menu'))
        send_photo_message(chat_id, message_id, usdt_text, keyboard)
    
    elif call.data == 'change_currency':
        currency_text = f"""
💱 <b>ВЫБОР ОСНОВНОЙ ВАЛЮТЫ</b>

<b>Выберите валюту для отображения баланса:</b>
• Rub — Российский рубль
• Usd — Доллар США
• Kzt — Казахстанский тенге
• Uah — Украинская гривна
• Byn — Белорусский рубль
• Ton — The open network
• Usdt — Tether
• Stars — Telegram Stars

<b>Ваша текущая валюта будет использоваться по умолчанию.</b>
        """
        send_photo_message(chat_id, message_id, currency_text, currency_menu_keyboard())
    
    elif call.data.startswith('currency_'):
        currency = call.data.split('_')[1]
        users[user_id]['currency'] = currency
        save_data()
        
        currency_updated_text = f"""
✅ <b>ВАЛЮТА ИЗМЕНЕНА</b>

<b>Новая основная валюта:</b> {currency}

<b>Теперь баланс будет отображаться в выбранной валюте.</b>
<i>При создании сделок вы можете выбрать любую доступную валюту.</i>
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("📊 Статистика", callback_data='stats_public'),
            InlineKeyboardButton("👤 Мой профиль", callback_data='my_profile')
        )
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, message_id, currency_updated_text, keyboard)
    
    elif call.data == 'create_deal':
        # ИЗМЕНЕНИЕ: Теперь показываем предупреждение вместо создания сделки
        warning_text, keyboard = warning_menu()
        send_photo_message(chat_id, message_id, warning_text, keyboard)
    
    elif call.data.startswith('method_'):
        currency = call.data.split('_')[1]
        users[user_id]['awaiting_deal_amount'] = True
        users[user_id]['current_deal'] = {
            'currency': currency,
            'seller_id': user_id
        }
        
        if currency == 'STARS':
            amount_text = f"""
💰 <b>УКАЖИТЕ КОЛИЧЕСТВО STARS</b>

<b>Telegram Stars — это внутренняя валюта Telegram</b>

<b>Примеры:</b>
• 100 (минимум)
• 500
• 1000

<b>Важно:</b>
• Stars не конвертируются в другие валюты
• Оплата происходит напрямую через Telegram
• Без комиссий за обмен

<b>Введите количество Stars:</b>
            """
        else:
            amount_text = f"""
💰 <b>УКАЖИТЕ СУММУ СДЕЛКИ</b>

<b>Примеры:</b>
• 5.75 (для ton/Usdt/Usd)
• 1500 (для Rub/Kzt)
• 500 (для Uah/Byn)

<b>Введите сумму:</b>
            """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='create_deal'))
        send_photo_message(chat_id, message_id, amount_text, keyboard)
    
    elif call.data.startswith('category_'):
        category = call.data.split('_')[1]
        
        category_names = {
            'gift': '🎁 Подарок',
            'nft': '🏷️ Nft тег',
            'channel': '📢 Канал/чат',
            'stars': '⭐ Stars'
        }
        
        users[user_id]['current_deal']['category'] = category_names.get(category, 'Товар')
        users[user_id]['awaiting_deal_category'] = True
        
        if category == 'gift':
            description_text = f"""
📝 <b>ОПИСАНИЕ ТОВАРА</b>

<b>Категория:</b> {category_names.get(category, 'Товар')}

<b>Опишите подробно что вы продаёте:</b>
• Что именно дарите
• Ссылка на подарок
• Дополнительные условия

<b>Пример:</b>
"Easter Egg", стоимость 500 руб.
Ссылка на подарок: https://t.me/nft/EasterEgg-158557

<b>Будьте максимально подробны и честны!</b>

<b>Введите описание:</b>
            """
        elif category == 'stars':
            description_text = f"""
📝 <b>ОПИСАНИЕ ТОВАРА</b>

<b>Категория:</b> {category_names.get(category, 'Товар')}

<b>Опишите подробно что вы продаёте:</b>
• Количество Stars
• Платформа (iOS/Android)
• Дополнительные условия

<b>Пример:</b>
"1000 Telegram Stars"

<b>Будьте максимально подробны и честны!</b>

<b>Введите описание:</b>
            """
        else:
            description_text = f"""
📝 <b>ОПИСАНИЕ ТОВАРА</b>

<b>Категория:</b> {category_names.get(category, 'Товар')}

<b>Опишите подробно что вы продаёте:</b>
• Для Nft тега: название тега, сеть
• Для канала/чата: ссылка, количество подписчиков

<b>Будьте максимально подробны и честны!</b>

<b>Введите описание:</b>
            """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='create_deal'))
        
        send_photo_message(chat_id, message_id, description_text, keyboard)
    
    elif call.data == 'referral':
        user = users[user_id]
        ref_link = f"https://t.me/{bot.get_me().username}?start={user['referral_id']}"
        ref_text = f"""
🎯 <b>РЕФЕРАЛЬНАЯ ПРОГРАММА</b>

<b>Ваша ссылка:</b>
{ref_link}

<b>Как это работает:</b>
1. Делитесь ссылкой с друзьями
2. Они регистрируются по вашей ссылке
3. Вы получаете 1% от каждой их сделки

<b>Ваши преимущества:</b>
• Пассивный доход
• Бонусы за активных рефералов
• Повышение рейтинга

<b>Приглашено:</b> 0 человек
<b>Заработано:</b> 0 {user['currency']}
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("📢 Поделиться", switch_inline_query=f"Присоединяйся к Playerok OTC! {ref_link}"),
            InlineKeyboardButton("🔙 В меню", callback_data='main_menu')
        )
        send_photo_message(chat_id, message_id, ref_text, keyboard)
    
    elif call.data == 'admin_panel':
        if user_id in admins or user_id in owners:
            admin_panel_text = f"""
⚙️ <b>АДМИН ПАНЕЛЬ PLAYEROK OTC</b>

<b>Управление системой:</b>
• Статистика бота
• Управление пользователей
• Управление сделками
• Модерация
• Управление воркерами
• Рассылка сообщений

<b>Выберите действие:</b>
            """
            send_photo_message(chat_id, message_id, admin_panel_text, admin_panel_menu(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
    
    elif call.data == 'worker_panel':
        if user_id in workers or user_id in admins or user_id in owners:
            worker_panel_text = f"""
👷 <b>ВОРКЕР ПАНЕЛЬ PLAYEROK OTC</b>

<b>Доступные действия:</b>
• Просмотр статистики
• Управление своими сделками
• Накрутка сделок (ограничено)
• Накрутка баланса (ограничено)
• Управление тегом для профитов

<b>Выберите действие:</b>
            """
            send_photo_message(chat_id, message_id, worker_panel_text, worker_panel_menu())
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён. Требуются права воркера", show_alert=True)
    
    elif call.data == 'worker_stats':
        if user_id in workers or user_id in admins or user_id in owners:
            user = users[user_id]
            user_tag = get_user_tag(user_id)
            
            stats_text = f"""
👷 <b>ВАША СТАТИСТИКА</b>

👤 <b>Воркер:</b> @{user['username']}
🏷️ <b>Тег:</b> {user_tag}
🆔 <b>ID:</b> <code>{user_id}</code>
📅 <b>В системе с:</b> {user['join_date']}
⏰ <b>Последняя активность:</b> {user['last_active']}

📊 <b>Общая статистика:</b>
• Успешных сделок: {user['success_deals']}
• Рейтинг: {user['rating']}⭐
• Споров выиграно: {user['disputes_won']}

💰 <b>Баланс:</b>
• Rub: {user['balance']['RUB']}
• Usd: {user['balance']['USD']}
• Ton: {user['balance']['TON']}
• Usdt: {user['balance']['USDT']}
• Stars: {user['balance']['STARS']}

<b>Доступные действия:</b>
            """
            send_photo_message(chat_id, message_id, stats_text, worker_panel_menu())
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
    
    elif call.data == 'worker_fake_deals':
        if user_id in workers or user_id in admins or user_id in owners:
            users[user_id]['awaiting_fake_deals'] = True
            fake_deals_text = """
💼 <b>НАКРУТКА СДЕЛОК (ВОРКЕР)</b>

<b>Введите количество сделок:</b>
• Максимум: 10 сделок за раз

<b>Формат:</b>
<code>5</code>

<b>Введите количество:</b>
            """
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='worker_panel'))
            
            send_photo_message(chat_id, message_id, fake_deals_text, keyboard)
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
    
    elif call.data == 'worker_fake_balance':
        if user_id in workers or user_id in admins or user_id in owners:
            users[user_id]['awaiting_fake_balance'] = True
            fake_balance_text = f"""
💰 <b>НАКРУТКА БАЛАНСА (ВОРКЕР)</b>

<b>Введите сумму и валюту:</b>
• Максимум: 1000 за раз
• Доступные валюты: Ton, Rub, Usd, Kzt, Uah, Byn, Usdt, STARS

<b>Формат:</b>
<code>500 Rub</code>
<code>100 Stars</code>
<code>50 Ton</code>

<b>Введите:</b>
            """
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='worker_panel'))
            
            send_photo_message(chat_id, message_id, fake_balance_text, keyboard)
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
    
    elif call.data == 'stats':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        active_users = sum(1 for u in users.values() if 
                          datetime.strptime(u['last_active'], "%d.%m.%Y %H:%M") > 
                          datetime.now().replace(hour=0, minute=0, second=0))
        
        stats_text = f"""
📊 <b>СТАТИСТИКА PLAYEROK OTC</b>

👥 <b>Пользователи:</b> {len(users)}
👑 <b>Владельцы:</b> {len(owners)}
⚙️ <b>Админы:</b> {len(admins) - len(owners)}
👷 <b>Воркеры:</b> {len(workers)}
🚫 <b>Заблокировано:</b> {len(blocked_users)}
📋 <b>Активных сделок:</b> {len(deals)}
👤 <b>Активных сегодня:</b> {active_users}

💰 <b>Оборот системы:</b>
⚡ Ton: {sum(u['balance']['TON'] for u in users.values()):.2f}
🇷🇺 Rub: {sum(u['balance']['RUB'] for u in users.values()):.2f}
🇺🇸 Usd: {sum(u['balance']['USD'] for u in users.values()):.2f}
🇰🇿 Kzt: {sum(u['balance']['KZT'] for u in users.values()):.2f}
🇺🇦 Uah: {sum(u['balance']['UAH'] for u in users.values()):.2f}
🇧🇾 Byn: {sum(u['balance']['BYN'] for u in users.values()):.2f}
💎 Usdt: {sum(u['balance']['USDT'] for u in users.values()):.2f}
⭐ Stars: {sum(u['balance']['STARS'] for u in users.values()):.0f}

📈 <b>За сегодня:</b>
• Новых пользователей: {len([u for u in users.values() if u['join_date'] == datetime.now().strftime("%d.%m.%Y")])}
• Завершённых сделок: {sum(1 for d in deals.values() if d.get('status') == 'completed' and d.get('created_at', '').startswith(datetime.now().strftime("%d.%m.%Y")))}
• Общий оборот: {sum(d.get('amount', 0) for d in deals.values() if d.get('status') == 'completed' and d.get('created_at', '').startswith(datetime.now().strftime("%d.%m.%Y"))):.2f} Usd

<b>Статистика активности:</b>
• Действий пользователей: {sum(len(v) for v in user_activities.values())}
• Действий в сделках: {sum(len(v) for v in deal_activities.values())}

<b>Стабильная работа:</b> 99.8%
<b>Данные сохранены:</b> ✅
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("🔄 Обновить", callback_data='stats'),
            InlineKeyboardButton("💾 Сохранить данные", callback_data='force_save')
        )
        keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
        send_photo_message(chat_id, message_id, stats_text, keyboard)
    
    elif call.data == 'force_save':
        if user_id in admins or user_id in owners:
            save_data()
            bot.answer_callback_query(call.id, "✅ Данные сохранены успешно!", show_alert=True)
            send_photo_message(chat_id, message_id, "✅ <b>ДАННЫЕ СОХРАНЕНЫ УСПЕШНО!</b>", admin_panel_menu(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
    
    elif call.data == 'show_users':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        if not users:
            send_photo_message(chat_id, message_id, "📭 Нет пользователей", admin_panel_menu(user_id))
            return
        
        users_text = f"""
👥 <b>СПИСОК ПОЛЬЗОВАТЕЛЕЙ</b>

<b>Всего:</b> {len(users)} пользователей

<b>Топ-5 по активности:</b>
        """
        
        sorted_users = sorted(users.items(), 
                             key=lambda x: datetime.strptime(x[1]['last_active'], "%d.%m.%Y %H:%M"), 
                             reverse=True)
        
        for idx, (uid, user_data) in enumerate(sorted_users[:5], 1):
            role = "👤"
            if uid in owners:
                role = "👑"
            elif uid in admins:
                role = "⚙️"
            elif uid in workers:
                role = "👷"
            
            # Добавляем статус блокировки
            if is_user_blocked(uid):
                role += " 🚫"
            
            users_text += f"\n{role} <b>{idx}. @{user_data['username']}</b>"
            users_text += f"\n   🆔 ID: {uid}"
            users_text += f"\n   ✅ Сделок: {user_data['success_deals']}"
            users_text += f"\n   ⭐ Рейтинг: {user_data['rating']}"
            users_text += f"\n   📅 Регистрация: {user_data['join_date']}"
            users_text += f"\n   ⏰ Активность: {user_data['last_active']}"
            users_text += f"\n   ───────────────────"
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("📥 Экспорт в Csv", callback_data='export_users'),
            InlineKeyboardButton("🔙 В админку", callback_data='admin_panel')
        )
        
        send_photo_message(chat_id, message_id, users_text, keyboard)
    
    elif call.data == 'show_admins':
        # Показываем список админов (только для владельцев)
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён. Только владельцы могут просматривать список админов", show_alert=True)
            return
        
        admins_text = f"""
👑 <b>СПИСОК АДМИНИСТРАТОРОВ</b>

<b>Всего:</b> {len(admins)} администраторов
<b>Владельцы:</b> {len(owners)}

<b>Страница:</b> 1
        """
        
        send_photo_message(chat_id, message_id, admins_text, admins_list_menu())
    
    elif call.data.startswith('show_admins_'):
        # Навигация по страницам списка админов
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        page = int(call.data.split('_')[2])
        admins_text = f"""
👑 <b>СПИСОК АДМИНИСТРАТОРОВ</b>

<b>Всего:</b> {len(admins)} администраторов
<b>Владельцы:</b> {len(owners)}

<b>Страница:</b> {page + 1}
        """
        
        send_photo_message(chat_id, message_id, admins_text, admins_list_menu(page))
    
    elif call.data.startswith('view_admin_'):
        # Просмотр информации об админе (только для владельцев)
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        admin_id = int(call.data.split('_')[2])
        if admin_id in users:
            show_user_profile(admin_id, chat_id, message_id)
    
    elif call.data.startswith('remove_admin_confirm_'):
        # Подтверждение удаления админа (только для владельцев)
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        admin_id = int(call.data.split('_')[3])
        
        # Не позволяем удалять владельцев
        if admin_id in owners:
            bot.answer_callback_query(call.id, "❌ Нельзя удалить владельца", show_alert=True)
            return
        
        if admin_id in admins:
            admins.remove(admin_id)
            save_data()
            
            # Логируем удаление администратора
            log_activity(user_id, f'Удалил администратора ID:{admin_id}')
            
            if admin_id in users:
                admin_name = users[admin_id]['username']
                notification_text = f"""
⚙️ <b>ВЫ БЫЛИ ЛИШЕНЫ СТАТУСА АДМИНИСТРАТОРА</b>

Ваш статус администратора был отозван владельцем.
Теперь вы являетесь обычным пользователем.

Если это ошибка, свяжитесь с владельцем.
                """
                try:
                    bot.send_message(admin_id, notification_text, parse_mode='HTML')
                except:
                    pass
            
            result_text = f"""
🗑️ <b>АДМИНИСТРАТОР УДАЛЁН</b>

<b>Администратор:</b> @{admin_name if admin_id in users else admin_id}
<b>ID:</b> <code>{admin_id}</code>
<b>Удалил:</b> @{users[user_id]['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус администратора успешно отозван.</b>
            """
            send_photo_message(chat_id, message_id, result_text, admin_panel_menu(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ Пользователь не является администратором", show_alert=True)
    
    elif call.data == 'remove_admin':
        # Удаление админа (только для владельцев)
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён. Только владельцы могут удалять администраторов", show_alert=True)
            return
        
        users[user_id]['awaiting_remove_worker'] = True  # Используем существующее поле
        remove_admin_text = f"""
🗑️ <b>УДАЛЕНИЕ АДМИНИСТРАТОРА</b>

<b>Введите ID администратора:</b>
• Можно получить через список администраторов
• Владельцев удалить нельзя

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, remove_admin_text, keyboard)
    
    elif call.data == 'show_workers':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        if not workers:
            send_photo_message(chat_id, message_id, "📭 Нет воркеров", admin_panel_menu(user_id))
            return
        
        workers_text = f"""
👷 <b>СПИСОК ВОРКЕРОВ</b>

<b>Всего:</b> {len(workers)} воркеров

        """
        
        for idx, worker_id in enumerate(list(workers)[:5], 1):
            if worker_id in users:
                user_data = users[worker_id]
                user_tag = get_user_tag(worker_id)
                workers_text += f"\n<b>{idx}. {user_tag}</b>"
                workers_text += f"\n   🆔 ID: {worker_id}"
                workers_text += f"\n   ✅ Сделок: {user_data['success_deals']}"
                workers_text += f"\n   ⭐ Рейтинг: {user_data['rating']}"
                workers_text += f"\n   📅 Регистрация: {user_data['join_date']}"
                workers_text += f"\n   ⏰ Активность: {user_data['last_active']}"
                workers_text += f"\n   ───────────────────"
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("👷 Добавить воркера", callback_data='add_worker'),
            InlineKeyboardButton("🗑️ Удалить воркера", callback_data='remove_worker')
        )
        keyboard.add(
            InlineKeyboardButton("🔍 Проверить сделки", callback_data='check_worker_deals'),
            InlineKeyboardButton("📉 Понизить воркера", callback_data='demote_worker')
        )
        keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, workers_text, keyboard)
    
    elif call.data == 'add_worker':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_worker_id'] = True
        worker_add_text = f"""
👷 <b>ДОБАВЛЕНИЕ ВОРКЕРА</b>

<b>Введите ID пользователя:</b>
• Можно получить через @userinfobot
• Или переслав сообщение пользователя

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, worker_add_text, keyboard)
    
    elif call.data == 'remove_worker':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_remove_worker'] = True
        remove_worker_text = f"""
🗑️ <b>УДАЛЕНИЕ ВОРКЕРА</b>

<b>Введите ID воркера:</b>
• Можно получить через список воркеров

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, remove_worker_text, keyboard)
    
    elif call.data.startswith('remove_worker_confirm_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        worker_id = int(call.data.split('_')[3])
        
        if worker_id in workers:
            workers.remove(worker_id)
            save_data()
            
            # Логируем удаление воркера
            log_activity(user_id, f'Удалил воркера ID:{worker_id}')
            
            if worker_id in users:
                worker_name = users[worker_id]['username']
                notification_text = f"""
❌ <b>ВЫ БЫЛИ ЛИШЕНЫ СТАТУСА ВОРКЕРА</b>

Ваш статус воркера был отозван администратором.
Теперь вы являетесь обычным пользователем.

Если это ошибка, свяжитесь с поддержкой.
                """
                try:
                    bot.send_message(worker_id, notification_text, parse_mode='HTML')
                except:
                    pass
            
            result_text = f"""
✅ <b>ВОРКЕР УДАЛЁН</b>

<b>Воркер:</b> @{worker_name if worker_id in users else worker_id}
<b>ID:</b> <code>{worker_id}</code>
<b>Удалил:</b> @{users[user_id]['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус воркера успешно отозван.</b>
            """
            send_photo_message(chat_id, message_id, result_text, admin_panel_menu(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ Пользователь не является воркером", show_alert=True)
    
    elif call.data == 'demote_worker':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_remove_worker'] = True
        demote_worker_text = f"""
📉 <b>ПОНИЖЕНИЕ ВОРКЕРА</b>

<b>Введите ID воркера:</b>
• Можно получить через список воркеров
• Воркер будет понижен до обычного пользователя

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, demote_worker_text, keyboard)
    
    elif call.data.startswith('demote_worker_confirm_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        worker_id = int(call.data.split('_')[3])
        
        if worker_id in workers:
            workers.remove(worker_id)
            save_data()
            
            # Логируем понижение воркера
            log_activity(user_id, f'Понизил воркера ID:{worker_id}')
            
            if worker_id in users:
                worker_name = users[worker_id]['username']
                notification_text = f"""
📉 <b>ВЫ БЫЛИ ПОНИЖЕНЫ</b>

Ваш статус воркера был понижен администратором.
Теперь вы являетесь обычным пользователем.

Если это ошибка, свяжитесь с поддержкой.
                """
                try:
                    bot.send_message(worker_id, notification_text, parse_mode='HTML')
                except:
                    pass
            
            result_text = f"""
📉 <b>ВОРКЕР ПОНИЖЕН</b>

<b>Воркер:</b> @{worker_name if worker_id in users else worker_id}
<b>ID:</b> <code>{worker_id}</code>
<b>Понизил:</b> @{users[user_id]['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус воркера успешно понижен до обычного пользователя.</b>
            """
            send_photo_message(chat_id, message_id, result_text, admin_panel_menu(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ Пользователь не является воркером", show_alert=True)
    
    elif call.data == 'check_worker_deals':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_check_deals'] = True
        check_deals_text = f"""
🔍 <b>ПРОВЕРКА СДЕЛОК ВОРКЕРА</b>

<b>Введите ID воркера:</b>
• Можно получить через список воркеров

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, check_deals_text, keyboard)
    
    elif call.data == 'add_admin':
        # Добавление админа (только для владельцев)
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён. Только владельцы могут добавлять администраторов", show_alert=True)
            return
        
        users[user_id]['awaiting_admin_id'] = True
        admin_add_text = f"""
👑 <b>ДОБАВЛЕНИЕ АДМИНИСТРАТОРА</b>

<b>Введите ID пользователя:</b>
• Можно получить через @userinfobot
• Или переслав сообщение пользователя

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, admin_add_text, keyboard)
    
    elif call.data == 'fake_deals':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_fake_deals'] = True
        fake_deals_text = f"""
💼 <b>НАКРУТКА СДЕЛОК</b>

<b>Введите данные:</b>
• ID пользователя
• Количество сделок

<b>Формат:</b>
<code>123456789 10</code>

<b>Введите:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, fake_deals_text, keyboard)
    
    elif call.data == 'fake_balance':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_fake_balance'] = True
        fake_balance_text = f"""
💰 <b>НАКРУТКА БАЛАНСА</b>

<b>Введите данные:</b>
• ID пользователя
• Сумма
• Валюта (Ton/Rub/Usd/Kzt/Uah/Byn/Usdt/STARS)

<b>Формат:</b>
<code>123456789 100 Rub</code>

<b>Введите:</b>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='admin_panel'))
        
        send_photo_message(chat_id, message_id, fake_balance_text, keyboard)
    
    elif call.data.startswith('pay_balance_'):
        deal_id = call.data.split('_')[2]
        if deal_id not in deals:
            bot.answer_callback_query(call.id, "❌ Сделка не найдена", show_alert=True)
            return
        
        deal = deals[deal_id]
        
        # Проверяем, может ли пользователь оплачивать
        if not can_user_pay(user_id):
            bot.answer_callback_query(call.id, "❌ К сожалению у вас не хватает средств", show_alert=True)
            return
        
        if deal['currency'] not in users[user_id]['balance']:
            users[user_id]['balance'][deal['currency']] = 0.0
            
        if users[user_id]['balance'][deal['currency']] < deal['amount']:
            bot.answer_callback_query(call.id, "❌ Недостаточно средств на балансе", show_alert=True)
            return
        
        users[user_id]['balance'][deal['currency']] -= deal['amount']
        
        if deal['currency'] not in users[deal['seller_id']]['balance']:
            users[deal['seller_id']]['balance'][deal['currency']] = 0.0
        users[deal['seller_id']]['balance'][deal['currency']] += deal['amount']
        
        deal['status'] = 'paid'
        save_data()
        
        # Логируем оплату сделки
        log_activity(user_id, 'Оплатил сделку с баланса', deal_id, f'Сумма: {deal["amount"]} {deal["currency"]}')
        
        buyer_text = f"""
✅ <b>ОПЛАТА ПОДТВЕРЖДЕНА</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
💰 <b>Списано:</b> {deal['amount']} {deal['currency']}

<b>Ожидайте отправки товара от продавца.</b>
<i>Обычно это занимает до 15 минут.</i>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📞 Поддержка", url='https://t.me/OfficialPlayerokSupport'))
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, message_id, buyer_text, keyboard)
        
        seller_text = f"""
💰 <b>ОПЛАТА ПОЛУЧЕНА!</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Покупатель:</b> @{users[user_id]['username']}
💸 <b>Сумма:</b> {deal['amount']} {deal['currency']}

Покупатель подтвердил оплату. Отправьте товар менеджеру!

🛡️ <b>Критически важное правило:</b>
Товар должен быть передан исключительно менеджеру - {MANAGER_USERNAME}!

🚫 <b>Если вам предлагают нарушить правило:</b>
• «Передайте напрямую покупателю/другому лицу»->
• Это мошенническая схема!
• Любая передача мимо менеджера:
1) Автоматически отменяет сделку
2) Лишает гарантий возврата средств

<b>После того как вы отправили товар техподдержке, нажмите кнопку снизу:</b>
        """
        seller_keyboard = InlineKeyboardMarkup(row_width=2)
        seller_keyboard.add(
            InlineKeyboardButton("✅ Я отправил товар", callback_data=f'sent_item_{deal_id}'),
            InlineKeyboardButton("⚠️ Проблема", callback_data=f'problem_{deal_id}')
        )
        
        send_photo_message(deal['seller_id'], None, seller_text, seller_keyboard)
    
    elif call.data.startswith('sent_item_'):
        deal_id = call.data.split('_')[2]
        if deal_id not in deals:
            bot.answer_callback_query(call.id, "❌ Сделка не найдена", show_alert=True)
            return
        
        deal = deals[deal_id]
        
        # Логируем отправку товара
        log_activity(user_id, 'Подтвердил отправку товара менеджеру', deal_id)
        
        seller_text = f"""
📤 <b>ОТПРАВКА ПОДТВЕРЖДЕНА</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Покупатель:</b> @{users[deal['buyer_id']]['username']}

<b>Товар отправлен менеджеру {MANAGER_USERNAME}.</b>
<i>Ожидайте подтверждения получения товара менеджером.</i>

<b>Внимание:</b> Любая передача товара напрямую покупателю автоматически отменяет сделку!
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, message_id, seller_text, keyboard)
        
        # Уведомляем админов о получении товара
        notify_admins_item_received(deal_id, user_id)
        
        buyer_text = f"""
📦 <b>ОЖИДАНИЕ ПОДТВЕРЖДЕНИЯ</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{users[deal['seller_id']]['username']}

<b>Продавец отправил товар менеджеру.</b>
<i>Администратор проверяет получение товара.</i>

<b>Внимание:</b> Любая передача товара напрямую от продавца автоматически отменяет сделку!

<b>Ожидайте подтверждения от администратора.</b>
        """
        buyer_keyboard = InlineKeyboardMarkup(row_width=1)
        buyer_keyboard.add(InlineKeyboardButton("📞 Поддержка", url='https://t.me/OfficialPlayerokSupport'))
        
        # Отправляем сообщение покупателю
        send_photo_message(deal['buyer_id'], None, buyer_text, buyer_keyboard)
    
    elif call.data.startswith('confirm_pay_'):
        deal_id = call.data.split('_')[2]
        if deal_id not in deals:
            bot.answer_callback_query(call.id, "❌ Сделка не найдена", show_alert=True)
            return
        
        deal = deals[deal_id]
        deal['status'] = 'paid'
        save_data()
        
        # Логируем подтверждение оплаты
        log_activity(user_id, 'Подтвердил оплату сделки', deal_id)
        
        seller_text = f"""
💰 <b>ОПЛАТА ПОЛУЧЕНА!</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Покупатель:</b> @{users[user_id]['username']}
💸 <b>Сумма:</b> {deal['amount']} {deal['currency']}

Покупатель подтвердил оплату. Отправьте товар менеджеру!

🛡️ <b>Критически важное правило:</b>
Товар должен быть передан исключительно менеджеру - {MANAGER_USERNAME}!

🚫 <b>Если вам предлагают нарушить правило:</b>
• «Передайте напрямую покупателю/другому лицу»->
• Это мошенническая схема!
• Любая передача мимо менеджера:
1) Автоматически отменяет сделку
2) Лишает гарантий возврата средств

<b>После того как вы отправили товар техподдержке, нажмите кнопку снизу:</b>
        """
        seller_keyboard = InlineKeyboardMarkup(row_width=2)
        seller_keyboard.add(
            InlineKeyboardButton("✅ Я отправил товар", callback_data=f'sent_item_{deal_id}'),
            InlineKeyboardButton("📞 Поддержка", url='https://t.me/OfficialPlayerokSupport')
        )
        
        send_photo_message(deal['seller_id'], None, seller_text, seller_keyboard)
        
        buyer_text = f"""
✅ <b>ОПЛАТА ПОДТВЕРЖДЕНА</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Продавец:</b> @{users[deal['seller_id']]['username']}
💸 <b>Сумма:</b> {deal['amount']} {deal['currency']}

<b>Ожидайте отправки товара менеджеру от продавца.</b>
<i>Продавец получил уведомление о вашей оплате.</i>

<b>Внимание:</b> Любая передача товара напрямую от продавца автоматически отменяет сделку!
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📞 Поддержка", url='https://t.me/OfficialPlayerokSupport'))
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, message_id, buyer_text, keyboard)
    
    elif call.data.startswith('dispute_'):
        deal_id = call.data.split('_')[1]
        if deal_id not in deals:
            bot.answer_callback_query(call.id, "❌ Сделка не найдена", show_alert=True)
            return
        
        dispute_text = f"""
⚠️ <b>ОТКРЫТИЕ СПОРА</b>

📋 <b>Сделка:</b> #{deal_id[:8]}
👤 <b>Ваша роль:</b> {'Покупатель' if user_id == deals[deal_id].get('buyer_id') else 'Продавец'}
👨‍💼 <b>Менеджер сделки:</b> {MANAGER_USERNAME}

<b>Вы уверены, что хотите открыть спор?</b>
<i>Администратор рассмотрит ваш спор в течение 24 часов.</i>

<b>Выберите причину:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("❌ Не оплатил", callback_data=f'dispute_nopay_{deal_id}'),
            InlineKeyboardButton("📦 Не отправил", callback_data=f'dispute_nosend_{deal_id}')
        )
        keyboard.add(
            InlineKeyboardButton("🔄 Не тот товар", callback_data=f'dispute_wrong_{deal_id}'),
            InlineKeyboardButton("🚫 Другое", callback_data=f'dispute_other_{deal_id}')
        )
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data=f'view_deal_{deal_id}'))
        
        send_photo_message(chat_id, message_id, dispute_text, keyboard)
    
    # Новые функции админа: просмотр всех сделок
    elif call.data == 'all_deals_admin':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        show_all_deals_admin(user_id, chat_id, message_id)
    
    elif call.data.startswith('all_deals_admin_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        page = int(call.data.split('_')[3])
        show_all_deals_admin(user_id, chat_id, message_id, page)
    
    elif call.data.startswith('admin_view_deal_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        deal_id = call.data.split('_')[3]
        show_deal_details_admin(user_id, chat_id, message_id, deal_id)
    
    # Просмотр действий в сделке
    elif call.data == 'deal_activities_admin':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        activities_text = """
🔍 <b>ПРОСМОТР ДЕЙСТВИЙ В СДЕЛКЕ</b>

<b>Выберите сделку для просмотра истории действий:</b>
• Отображаются только сделки с зафиксированными действиями
• Для каждой сделки показано количество действий
        """
        
        send_photo_message(chat_id, message_id, activities_text, deal_activities_menu_keyboard())
    
    elif call.data.startswith('deal_activities_menu_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        page = int(call.data.split('_')[3])
        activities_text = f"""
🔍 <b>ПРОСМОТР ДЕЙСТВИЙ В СДЕЛКЕ</b>

<b>Страница:</b> {page + 1}
<b>Выберите сделку для просмотра истории действий:</b>
        """
        
        send_photo_message(chat_id, message_id, activities_text, deal_activities_menu_keyboard(page))
    
    elif call.data.startswith('admin_deal_activity_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        parts = call.data.split('_')
        deal_id = parts[3]
        page = int(parts[4]) if len(parts) > 4 else 0
        show_deal_activities_admin(user_id, chat_id, message_id, deal_id, page)
    
    # Просмотр действий пользователя
    elif call.data == 'user_activities_admin':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        activities_text = """
👤 <b>ПРОСМОТР ДЕЙСТВИЙ ПОЛЬЗОВАТЕЛЯ</b>

<b>Выберите пользователя для просмотра истории действий:</b>
• Отображаются только пользователи с зафиксированными действиями
• Для каждого пользователя показано количество действий
        """
        
        send_photo_message(chat_id, message_id, activities_text, user_activities_menu_keyboard())
    
    elif call.data.startswith('user_activities_menu_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        page = int(call.data.split('_')[3])
        activities_text = f"""
👤 <b>ПРОСМОТР ДЕЙСТВИЙ ПОЛЬЗОВАТЕЛЯ</b>

<b>Страница:</b> {page + 1}
<b>Выберите пользователя для просмотра истории действий:</b>
        """
        
        send_photo_message(chat_id, message_id, activities_text, user_activities_menu_keyboard(page))
    
    elif call.data.startswith('admin_user_activity_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        parts = call.data.split('_')
        target_user_id = int(parts[3])
        page = int(parts[4]) if len(parts) > 4 else 0
        show_user_activities_admin(user_id, chat_id, message_id, target_user_id, page)
    
    elif call.data.startswith('admin_view_user_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        target_user_id = int(call.data.split('_')[3])
        if target_user_id in users:
            show_user_profile(target_user_id, chat_id, message_id)
    
    # Меню рассылок
    elif call.data == 'broadcast_menu':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        broadcast_text = """
📢 <b>РАССЫЛКА СООБЩЕНИЙ</b>

<b>Выберите тип рассылки:</b>
• Всем пользователям — сообщение получит каждый зарегистрированный пользователь
• Только воркерам — сообщение получат все воркеры
• Только админам — сообщение получат все администраторы
• Конкретному пользователю — личное сообщение одному пользователю

<b>Внимание:</b> Массовая рассылка может занять некоторое время!
        """
        
        send_photo_message(chat_id, message_id, broadcast_text, broadcast_menu_keyboard())
    
    elif call.data.startswith('broadcast_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        broadcast_type = call.data.split('_')[1]
        awaiting_broadcast_message[user_id] = broadcast_type
        
        if broadcast_type == 'all':
            recipient_text = "всем пользователям"
            count = len(users)
        elif broadcast_type == 'workers':
            recipient_text = "всем воркерам"
            count = len(workers)
        elif broadcast_type == 'admins':
            recipient_text = "всем администраторам"
            count = len(admins)
        else:
            recipient_text = "получателям"
            count = 0
        
        broadcast_instruction = f"""
✉️ <b>ПОДГОТОВКА РАССЫЛКИ</b>

<b>Тип рассылки:</b> {recipient_text}
<b>Количество получателей:</b> {count}

<b>Отправьте сообщение для рассылки:</b>
• Поддерживается HTML-разметка
• Можно отправлять текст, фото, документы
• Для отмены нажмите /cancel

<b>Пример сообщения:</b>
<code>🎉 Новое обновление системы!
Добавлены новые функции и улучшена безопасность.</code>

<b>Отправьте ваше сообщение:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='broadcast_menu'))
        
        send_photo_message(chat_id, message_id, broadcast_instruction, keyboard)
    
    elif call.data == 'private_message_menu':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        private_message_text = """
✉️ <b>ЛИЧНОЕ СООБЩЕНИЕ</b>

<b>Выберите действие:</b>
• Написать пользователю — отправить сообщение конкретному пользователю
• Список получателей — просмотреть всех пользователей для выбора

<b>Личное сообщение отправляется от имени бота.</b>
        """
        
        send_photo_message(chat_id, message_id, private_message_text, private_message_menu_keyboard())
    
    elif call.data == 'private_message':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        awaiting_private_message[user_id] = True
        
        private_message_instruction = """
👤 <b>ЛИЧНОЕ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЮ</b>

<b>Введите ID пользователя и сообщение:</b>
• Формат: <code>123456789 Ваше сообщение здесь</code>
• ID можно получить из профиля пользователя
• Или используйте список получателей для выбора

<b>Пример:</b>
<code>1521791703 Привет! Это тестовое сообщение от администратора.</code>

<b>Введите ID и сообщение:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📋 Список получателей", callback_data='private_message_list_0'))
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='private_message_menu'))
        
        send_photo_message(chat_id, message_id, private_message_instruction, keyboard)
    
    elif call.data == 'private_message_list':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        recipients_text = """
📋 <b>СПИСОК ПОЛУЧАТЕЛЕЙ</b>

<b>Выберите пользователя для отправки сообщения:</b>
• 👤 — обычный пользователь
• 👷 — воркер
• ⚙️ — администратор
• 👑 — владелец

<b>Нажмите на пользователя, чтобы выбрать его в качестве получателя.</b>
        """
        
        send_photo_message(chat_id, message_id, recipients_text, private_message_recipients_keyboard())
    
    elif call.data.startswith('private_message_list_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        page = int(call.data.split('_')[3])
        recipients_text = f"""
📋 <b>СПИСОК ПОЛУЧАТЕЛЕЙ</b>

<b>Страница:</b> {page + 1}
<b>Выберите пользователя для отправки сообщения:</b>
        """
        
        send_photo_message(chat_id, message_id, recipients_text, private_message_recipients_keyboard(page))
    
    elif call.data.startswith('select_recipient_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        recipient_id = int(call.data.split('_')[2])
        awaiting_private_message[user_id] = recipient_id
        
        recipient = users.get(recipient_id, {'username': f'ID:{recipient_id}'})
        
        recipient_text = f"""
✅ <b>ПОЛУЧАТЕЛЬ ВЫБРАН</b>

<b>Пользователь:</b> @{recipient['username']}
<b>ID:</b> <code>{recipient_id}</code>

<b>Теперь отправьте сообщение для этого пользователя:</b>
• Поддерживается HTML-разметка
• Можно отправлять текст, фото, документы
• Для отмены нажмите /cancel

<b>Отправьте ваше сообщение:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Выбрать другого", callback_data='private_message_list_0'))
        
        send_photo_message(chat_id, message_id, recipient_text, keyboard)
    
    elif call.data.startswith('admin_message_user_'):
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        target_user_id = int(call.data.split('_')[3])
        awaiting_private_message[user_id] = target_user_id
        
        target_user = users.get(target_user_id, {'username': f'ID:{target_user_id}'})
        
        message_text = f"""
✉️ <b>СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЮ</b>

<b>Получатель:</b> @{target_user['username']}
<b>ID:</b> <code>{target_user_id}</code>

<b>Отправьте сообщение для этого пользователя:</b>
• Поддерживается HTML-разметка
• Можно отправлять текст, фото, документы
• Для отмены нажмите /cancel

<b>Отправьте ваше сообщение:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data=f'admin_user_activity_{target_user_id}_0'))
        
        send_photo_message(chat_id, message_id, message_text, keyboard)
    
    # Обработчики поиска
    elif call.data == 'search_deal_admin':
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_search_deal'] = True
        search_text = """
🔍 <b>ПОИСК СДЕЛКИ</b>

<b>Введите ID сделки или часть ID:</b>
• Полный ID: <code>123e4567-e89b-12d3-a456-426614174000</code>
• Короткий ID: <code>123e4567</code>

<b>Введите ID для поиска:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='all_deals_admin'))
        
        send_photo_message(chat_id, message_id, search_text, keyboard)
    
    elif call.data in ['search_deal_activity_admin', 'search_user_activity_admin', 'search_recipient_admin']:
        if user_id not in admins and user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        search_type = call.data.replace('_admin', '')
        users[user_id][f'awaiting_search_{search_type}'] = True
        
        if 'deal' in search_type:
            search_text = """
🔍 <b>ПОИСК СДЕЛКИ ДЛЯ ПРОСМОТРА АКТИВНОСТИ</b>

<b>Введите ID сделки или часть ID:</b>
• Полный ID: <code>123e4567-e89b-12d3-a456-426614174000</code>
• Короткий ID: <code>123e4567</code>

<b>Введите ID для поиска:</b>
            """
            back_button = 'deal_activities_admin'
        elif 'user' in search_type or 'recipient' in search_type:
            search_text = """
🔍 <b>ПОИСК ПОЛЬЗОВАТЕЛЯ</b>

<b>Введите ID пользователя или username:</b>
• ID: <code>123456789</code>
• Username: <code>username</code> (без @)

<b>Введите данные для поиска:</b>
            """
            back_button = 'user_activities_admin' if 'user' in search_type else 'private_message_menu'
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data=back_button))
        
        send_photo_message(chat_id, message_id, search_text, keyboard)
    
    # НОВЫЕ ФУНКЦИИ: Управление блокировками
    elif call.data == 'block_user_menu':
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён. Только владельцы могут управлять блокировками", show_alert=True)
            return
        
        block_menu_text = """
🚫 <b>УПРАВЛЕНИЕ БЛОКИРОВКАМИ</b>

<b>Выберите действие:</b>
• Заблокировать пользователя — полностью отключить доступ к боту
• Разблокировать пользователя — восстановить доступ
• Список заблокированных — просмотреть всех заблокированных пользователей

<b>Внимание:</b> Блокировка применяется ко всем уровням пользователей (включая администраторов и воркеров)
        """
        
        send_photo_message(chat_id, message_id, block_menu_text, block_user_menu_keyboard())
    
    elif call.data == 'block_user':
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_block_user'] = True
        block_user_text = """
🚫 <b>БЛОКИРОВКА ПОЛЬЗОВАТЕЛЯ</b>

<b>Введите ID пользователя:</b>
• Можно заблокировать любого пользователя (включая администраторов и воркеров)
• Пользователь потеряет доступ ко всем функциям бота
• Для разблокировки потребуется действие владельца

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID пользователя для блокировки:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='block_user_menu'))
        
        send_photo_message(chat_id, message_id, block_user_text, keyboard)
    
    elif call.data == 'unblock_user':
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        users[user_id]['awaiting_unblock_user'] = True
        unblock_user_text = """
✅ <b>РАЗБЛОКИРОВКА ПОЛЬЗОВАТЕЛЯ</b>

<b>Введите ID пользователя:</b>
• Пользователь получит доступ к функциям бота согласно своему уровню
• Уровень пользователя сохраняется после разблокировки

<b>Формат:</b>
<code>123456789</code>

<b>Введите ID пользователя для разблокировки:</b>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data='block_user_menu'))
        
        send_photo_message(chat_id, message_id, unblock_user_text, keyboard)
    
    elif call.data == 'blocked_users_list':
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        blocked_text = f"""
🚫 <b>СПИСОК ЗАБЛОКИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ</b>

<b>Всего заблокировано:</b> {len(blocked_users)} пользователей

<b>Страница:</b> 1
        """
        
        send_photo_message(chat_id, message_id, blocked_text, blocked_users_list_keyboard())
    
    elif call.data.startswith('blocked_list_'):
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        page = int(call.data.split('_')[2])
        blocked_text = f"""
🚫 <b>СПИСОК ЗАБЛОКИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ</b>

<b>Всего заблокировано:</b> {len(blocked_users)} пользователей

<b>Страница:</b> {page + 1}
        """
        
        send_photo_message(chat_id, message_id, blocked_text, blocked_users_list_keyboard(page))
    
    elif call.data.startswith('view_blocked_'):
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        blocked_id = int(call.data.split('_')[2])
        if blocked_id in users:
            user = users[blocked_id]
            role = "👤 Пользователь"
            if blocked_id in owners:
                role = "👑 Владелец"
            elif blocked_id in admins:
                role = "⚙️ Администратор"
            elif blocked_id in workers:
                role = "👷 Воркер"
            
            blocked_info_text = f"""
🚫 <b>ИНФОРМАЦИЯ О ЗАБЛОКИРОВАННОМ ПОЛЬЗОВАТЕЛЕ</b>

<b>Пользователь:</b> @{user['username']}
<b>ID:</b> <code>{blocked_id}</code>
<b>Уровень:</b> {role}
<b>Статус:</b> Заблокирован 🚫
<b>Дата регистрации:</b> {user['join_date']}
<b>Последняя активность:</b> {user['last_active']}
<b>Успешных сделок:</b> {user['success_deals']}
<b>Рейтинг:</b> {user['rating']}⭐

<b>Доступ к боту:</b> Полностью отключен
            """
            
            send_photo_message(chat_id, message_id, blocked_info_text, blocked_user_management_menu(blocked_id))
    
    elif call.data.startswith('block_user_'):
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        target_user_id = int(call.data.split('_')[2])
        
        if target_user_id in blocked_users:
            bot.answer_callback_query(call.id, "⚠️ Пользователь уже заблокирован", show_alert=True)
            return
        
        # Блокируем пользователя
        blocked_users.add(target_user_id)
        save_data()
        
        # Логируем блокировку
        log_activity(user_id, f'Заблокировал пользователя ID:{target_user_id}')
        
        # Отправляем уведомление пользователю
        if target_user_id in users:
            user_name = users[target_user_id]['username']
            block_notification = f"""
🚫 <b>ВЫ БЫЛИ ЗАБЛОКИРОВАНЫ</b>

Ваш аккаунт был заблокирован владельцем системы.
Вы потеряли доступ ко всем функциям бота.

<b>Причина блокировки:</b> Нарушение правил системы
<b>Заблокировал:</b> Владелец системы
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

Для выяснения причин и возможной разблокировки обратитесь к владельцу.
            """
            try:
                bot.send_message(target_user_id, block_notification, parse_mode='HTML')
            except:
                pass
        
        result_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН</b>

<b>Пользователь:</b> @{user_name if target_user_id in users else target_user_id}
<b>ID:</b> <code>{target_user_id}</code>
<b>Заблокировал:</b> @{users[user_id]['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь полностью потерял доступ к боту.</b>
<i>Уведомление отправлено пользователю.</i>
        """
        
        send_photo_message(chat_id, message_id, result_text, block_user_menu_keyboard())
    
    elif call.data.startswith('unblock_user_'):
        if user_id not in owners:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён", show_alert=True)
            return
        
        target_user_id = int(call.data.split('_')[2])
        
        if target_user_id not in blocked_users:
            bot.answer_callback_query(call.id, "⚠️ Пользователь не заблокирован", show_alert=True)
            return
        
        # Разблокируем пользователя
        blocked_users.remove(target_user_id)
        save_data()
        
        # Логируем разблокировку
        log_activity(user_id, f'Разблокировал пользователя ID:{target_user_id}')
        
        # Отправляем уведомление пользователю
        if target_user_id in users:
            user_name = users[target_user_id]['username']
            unblock_notification = f"""
✅ <b>ВЫ БЫЛИ РАЗБЛОКИРОВАНЫ</b>

Ваш аккаунт был разблокирован владельцем системы.
Доступ ко всем функциям бота восстановлен.

<b>Разблокировал:</b> Владелец системы
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Ваш уровень доступа:</b>
"""
            # Добавляем информацию об уровне пользователя
            if target_user_id in owners:
                unblock_notification += "👑 Владелец"
            elif target_user_id in admins:
                unblock_notification += "⚙️ Администратор"
            elif target_user_id in workers:
                unblock_notification += "👷 Воркер"
            else:
                unblock_notification += "👤 Пользователь"
            
            unblock_notification += "\n\nДобро пожаловать обратно в систему!"
            
            try:
                bot.send_message(target_user_id, unblock_notification, parse_mode='HTML')
            except:
                pass
        
        result_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ РАЗБЛОКИРОВАН</b>

<b>Пользователь:</b> @{user_name if target_user_id in users else target_user_id}
<b>ID:</b> <code>{target_user_id}</code>
<b>Разблокировал:</b> @{users[user_id]['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Доступ пользователя к боту восстановлен.</b>
<i>Уведомление отправлено пользователю.</i>
        """
        
        send_photo_message(chat_id, message_id, result_text, block_user_menu_keyboard())
    
    elif call.data == 'noop':
        # Пустое действие, используется для кнопок-заглушек
        bot.answer_callback_query(call.id)
    
    else:
        # Если callback не распознан, показываем главное меню
        welcome_text, keyboard = main_menu(user_id)
        send_photo_message(chat_id, message_id, welcome_text, keyboard)

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Проверяем блокировку
    if is_user_blocked(user_id):
        blocked_text = """
🚫 <b>ВЫ ЗАБЛОКИРОВАНЫ</b>

Ваш аккаунт был заблокирован администрацией.
Вы не можете использовать функционал бота.

Для выяснения причин обратитесь к администратору.
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📞 Связь с администрацией", url='https://t.me/OfficialPlayerokSupport'))
        bot.send_message(chat_id, blocked_text, parse_mode='HTML', reply_markup=keyboard)
        return
    
    # Игнорируем сообщения не от пользователя (например, из групп)
    if message.chat.type != 'private':
        return
    
    init_user(user_id)
    update_user_activity(user_id)
    user = users[user_id]
    
    # НОВЫЙ ОБРАБОТЧИК: Установка тега
    if user.get('awaiting_set_tag'):
        tag = message.text.strip()
        
        # Проверяем формат тега
        if not tag.startswith('#'):
            bot.send_message(chat_id, "❌ <b>ТЕГ ДОЛЖЕН НАЧИНАТЬСЯ С СИМВОЛА #</b>\n\nПример: #best_worker", parse_mode='HTML')
            return
        
        if len(tag) < 2:
            bot.send_message(chat_id, "❌ <b>ТЕГ СЛИШКОМ КОРОТКИЙ</b>\n\nМинимум 2 символа (включая #)", parse_mode='HTML')
            return
        
        if len(tag) > 20:
            bot.send_message(chat_id, "❌ <b>ТЕГ СЛИШКОМ ДЛИННЫЙ</b>\n\nМаксимум 20 символов", parse_mode='HTML')
            return
        
        # Проверяем, не используется ли тег другим пользователем
        for uid, existing_tag in user_tags.items():
            if existing_tag == tag and uid != user_id:
                bot.send_message(chat_id, f"❌ <b>ТЕГ УЖЕ ИСПОЛЬЗУЕТСЯ</b>\n\nТег {tag} уже используется другим пользователем", parse_mode='HTML')
                return
        
        # Сохраняем тег
        user_tags[user_id] = tag
        save_data()
        
        # Логируем установку тега
        log_activity(user_id, 'Установил тег', details=f'Тег: {tag}')
        
        users[user_id]['awaiting_set_tag'] = False
        
        tag_success_text = f"""
✅ <b>ТЕГ УСТАНОВЛЕН!</b>

<b>Ваш тег:</b> {tag}

<b>Теперь в профитах будет отображаться:</b>
"Воркер: {tag}" вместо "Воркер: @{user['username']}"

<i>Тег будет использоваться во всех новых профитах.</i>
        """
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("🏷️ Управление тегом", callback_data='my_tag'),
            InlineKeyboardButton("🔙 В меню", callback_data='main_menu')
        )
        
        send_photo_message(chat_id, None, tag_success_text, keyboard)
        return
    
    # НОВЫЙ ОБРАБОТЧИК: Получение информации о скаме от админа
    if user_id in awaiting_scam_info:
        deal_id = awaiting_scam_info[user_id]
        
        if deal_id not in deals:
            bot.send_message(chat_id, "❌ <b>СДЕЛКА НЕ НАЙДЕНА</b>\n\nСделка была удалена или не существует.", parse_mode='HTML')
            del awaiting_scam_info[user_id]
            return
        
        scam_info = message.text.strip()
        
        if len(scam_info) < 5:
            bot.send_message(chat_id, "❌ <b>СЛИШКОМ КОРОТКОЕ ОПИСАНИЕ</b>\n\nОпишите подробнее на что заскамили (минимум 5 символов).", parse_mode='HTML')
            return
        
        # Завершаем сделку с информацией о скаме
        if complete_deal_with_scam_info(deal_id, scam_info, user_id):
            result_text = f"""
✅ <b>СДЕЛКА ЗАВЕРШЕНА С ПРОФИТОМ!</b>

📋 <b>ID сделки:</b> #{deal_id[:8]}
📝 <b>На что заскамили:</b> {scam_info}

<b>Информация отправлена:</b>
1. В форум логов (раздел профитов)
2. В группу профитов (без личного кода)
3. Воркеру с личным кодом для выплаты

<b>Профит успешно зарегистрирован в системе!</b>
            """
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton("📋 Все сделки", callback_data='all_deals_admin'),
                InlineKeyboardButton("⚙️ В админку", callback_data='admin_panel')
            )
            
            send_photo_message(chat_id, None, result_text, keyboard)
        else:
            bot.send_message(chat_id, "❌ <b>ОШИБКА ЗАВЕРШЕНИЯ СДЕЛКИ</b>\n\nНе удалось завершить сделку.", parse_mode='HTML')
        
        del awaiting_scam_info[user_id]
        return
    
    # Проверяем, является ли пользователь администратором/владельцем и ожидает ли он действий
    if user_id in admins or user_id in owners:
        # Обработка поиска сделки
        if user.get('awaiting_search_deal'):
            search_query = message.text.strip()
            users[user_id]['awaiting_search_deal'] = False
            
            # Поиск сделки по ID
            found_deals = []
            for deal_id in deals.keys():
                if search_query.lower() in deal_id.lower():
                    found_deals.append(deal_id)
            
            if not found_deals:
                bot.send_message(chat_id, f"❌ <b>СДЕЛКИ НЕ НАЙДЕНЫ</b>\n\nПо запросу '{search_query}' не найдено ни одной сделки.", parse_mode='HTML')
                show_all_deals_admin(user_id, chat_id)
                return
            
            if len(found_deals) == 1:
                # Если найдена одна сделка, показываем ее детали
                show_deal_details_admin(user_id, chat_id, None, found_deals[0])
                return
            else:
                # Если найдено несколько сделок, показываем список
                deals_text = f"🔍 <b>РЕЗУЛЬТАТЫ ПОИСКА СДЕЛОК</b>\n\n"
                deals_text += f"<b>Найдено сделок:</b> {len(found_deals)}\n"
                deals_text += f"<b>Запрос:</b> '{search_query}'\n\n"
                
                for i, deal_id in enumerate(found_deals[:10], 1):
                    deal = deals[deal_id]
                    seller = users.get(deal['seller_id'], {'username': 'Неизвестно'})
                    deals_text += f"{i}. <b>Сделка #{deal_id[:8]}</b>\n"
                    deals_text += f"   Сумма: {deal['amount']} {deal['currency']}\n"
                    deals_text += f"   Продавец: @{seller['username']}\n"
                    deals_text += f"   Статус: {deal.get('status', 'Неизвестно')}\n"
                    deals_text += "   ───────────────────\n"
                
                if len(found_deals) > 10:
                    deals_text += f"\n<i>И еще {len(found_deals) - 10} сделок...</i>\n"
                
                keyboard = InlineKeyboardMarkup(row_width=1)
                for deal_id in found_deals[:5]:
                    keyboard.add(InlineKeyboardButton(f"📄 Сделка #{deal_id[:8]}", callback_data=f'admin_view_deal_{deal_id}'))
                
                keyboard.add(InlineKeyboardButton("🔙 Все сделки", callback_data='all_deals_admin'))
                
                send_photo_message(chat_id, None, deals_text, keyboard)
                return
        
        # Обработка поиска сделки для активности
        elif user.get('awaiting_search_deal_activity'):
            search_query = message.text.strip()
            users[user_id]['awaiting_search_deal_activity'] = False
            
            # Поиск сделки с активностью
            found_deals = []
            for deal_id in deal_activities.keys():
                if search_query.lower() in deal_id.lower():
                    found_deals.append(deal_id)
            
            if not found_deals:
                bot.send_message(chat_id, f"❌ <b>СДЕЛКИ С АКТИВНОСТЬЮ НЕ НАЙДЕНЫ</b>\n\nПо запросу '{search_query}' не найдено сделок с активностью.", parse_mode='HTML')
                send_photo_message(chat_id, None, "🔍 <b>ПРОСМОТР ДЕЙСТВИЙ В СДЕЛКЕ</b>", deal_activities_menu_keyboard())
                return
            
            if len(found_deals) == 1:
                # Если найдена одна сделка, показываем ее активность
                show_deal_activities_admin(user_id, chat_id, None, found_deals[0])
                return
            else:
                # Если найдено несколько сделок, показываем список
                deals_text = f"🔍 <b>РЕЗУЛЬТАТЫ ПОИСКА СДЕЛОК С АКТИВНОСТЬЮ</b>\n\n"
                deals_text += f"<b>Найдено сделок:</b> {len(found_deals)}\n"
                deals_text += f"<b>Запрос:</b> '{search_query}'\n\n"
                
                for i, deal_id in enumerate(found_deals[:10], 1):
                    activity_count = len(deal_activities.get(deal_id, []))
                    deal = deals.get(deal_id, {})
                    deals_text += f"{i}. <b>Сделка #{deal_id[:8]}</b>\n"
                    deals_text += f"   Действий: {activity_count}\n"
                    deals_text += f"   Статус: {deal.get('status', 'Неизвестно')}\n"
                    deals_text += "   ───────────────────\n"
                
                keyboard = InlineKeyboardMarkup(row_width=1)
                for deal_id in found_deals[:5]:
                    keyboard.add(InlineKeyboardButton(f"📊 #{deal_id[:8]} ({len(deal_activities.get(deal_id, []))})", callback_data=f'admin_deal_activity_{deal_id}_0'))
                
                keyboard.add(InlineKeyboardButton("🔙 К списку", callback_data='deal_activities_admin'))
                
                send_photo_message(chat_id, None, deals_text, keyboard)
                return
        
        # Обработка поиска пользователя для активности
        elif user.get('awaiting_search_user_activity') or user.get('awaiting_search_recipient'):
            search_type = 'user_activity' if user.get('awaiting_search_user_activity') else 'recipient'
            search_query = message.text.strip().lower()
            users[user_id][f'awaiting_search_{search_type}'] = False
            
            # Проверяем, является ли запрос числом (ID)
            if search_query.isdigit():
                # Поиск по ID
                user_id_to_find = int(search_query)
                if user_id_to_find in users:
                    found_users = [user_id_to_find]
                else:
                    found_users = []
            else:
                # Поиск по username
                found_users = []
                for uid, user_data in users.items():
                    if (search_query in user_data['username'].lower() or
                        search_query in f"@{user_data['username'].lower()}"):
                        found_users.append(uid)
            
            if not found_users:
                bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛИ НЕ НАЙДЕНЫ</b>\n\nПо запросу '{search_query}' не найдено пользователей.", parse_mode='HTML')
                
                if search_type == 'user_activity':
                    send_photo_message(chat_id, None, "👤 <b>ПРОСМОТР ДЕЙСТВИЙ ПОЛЬЗОВАТЕЛЯ</b>", user_activities_menu_keyboard())
                else:
                    send_photo_message(chat_id, None, "📋 <b>СПИСОК ПОЛУЧАТЕЛЕЙ</b>", private_message_recipients_keyboard())
                return
            
            if len(found_users) == 1:
                # Если найден один пользователь
                target_user_id = found_users[0]
                if search_type == 'user_activity':
                    show_user_activities_admin(user_id, chat_id, None, target_user_id)
                else:
                    awaiting_private_message[user_id] = target_user_id
                    recipient = users[target_user_id]
                    
                    recipient_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ НАЙДЕН</b>

<b>Пользователь:</b> @{recipient['username']}
<b>ID:</b> <code>{target_user_id}</code>

<b>Теперь отправьте сообщение для этого пользователя:</b>
• Поддерживается HTML-разметка
• Можно отправлять текст, фото, документы
• Для отмены нажмите /cancel

<b>Отправьте ваше сообщение:</b>
                    """
                    
                    keyboard = InlineKeyboardMarkup(row_width=1)
                    keyboard.add(InlineKeyboardButton("❌ Выбрать другого", callback_data='private_message_list_0'))
                    
                    send_photo_message(chat_id, None, recipient_text, keyboard)
                return
            else:
                # Если найдено несколько пользователей, показываем список
                users_text = f"🔍 <b>РЕЗУЛЬТАТЫ ПОИСКА ПОЛЬЗОВАТЕЛЕЙ</b>\n\n"
                users_text += f"<b>Найдено пользователей:</b> {len(found_users)}\n"
                users_text += f"<b>Запрос:</b> '{search_query}'\n\n"
                
                for i, uid in enumerate(found_users[:10], 1):
                    user_data = users[uid]
                    role_icon = "👑" if uid in owners else "⚙️" if uid in admins else "👷" if uid in workers else "👤"
                    activity_count = len(user_activities.get(uid, [])) if search_type == 'user_activity' else 0
                    
                    users_text += f"{i}. {role_icon} <b>@{user_data['username']}</b>\n"
                    users_text += f"   ID: <code>{uid}</code>\n"
                    if search_type == 'user_activity':
                        users_text += f"   Действий: {activity_count}\n"
                    users_text += f"   Сделок: {user_data['success_deals']}\n"
                    users_text += "   ───────────────────\n"
                
                keyboard = InlineKeyboardMarkup(row_width=1)
                for uid in found_users[:5]:
                    user_data = users[uid]
                    if search_type == 'user_activity':
                        keyboard.add(InlineKeyboardButton(f"👤 @{user_data['username'][:15]}", callback_data=f'admin_user_activity_{uid}_0'))
                    else:
                        keyboard.add(InlineKeyboardButton(f"👤 @{user_data['username'][:15]}", callback_data=f'select_recipient_{uid}'))
                
                if search_type == 'user_activity':
                    keyboard.add(InlineKeyboardButton("🔙 К списку", callback_data='user_activities_admin'))
                else:
                    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='private_message_menu'))
                
                send_photo_message(chat_id, None, users_text, keyboard)
                return
        
        # Обработка рассылки сообщений
        elif user_id in awaiting_broadcast_message:
            broadcast_type = awaiting_broadcast_message[user_id]
            
            if message.text and message.text.strip() == '/cancel':
                del awaiting_broadcast_message[user_id]
                send_photo_message(chat_id, None, "❌ <b>РАССЫЛКА ОТМЕНЕНА</b>", broadcast_menu_keyboard())
                return
            
            # Определяем получателей
            if broadcast_type == 'all':
                recipients = list(users.keys())
                recipient_type = "всем пользователям"
            elif broadcast_type == 'workers':
                recipients = list(workers)
                recipient_type = "воркерам"
            elif broadcast_type == 'admins':
                recipients = list(admins)
                recipient_type = "администраторам"
            else:
                recipients = []
                recipient_type = "получателям"
            
            # Убираем отправителя из получателей
            if user_id in recipients:
                recipients.remove(user_id)
            
            if not recipients:
                bot.send_message(chat_id, "❌ <b>НЕТ ПОЛУЧАТЕЛЕЙ</b>\n\nДля выбранного типа рассылки не найдено получателей.", parse_mode='HTML')
                del awaiting_broadcast_message[user_id]
                return
            
            # Подготавливаем сообщение
            message_text = message.text or message.caption or ""
            parse_mode = 'HTML'
            
            # Отправляем сообщение получателям
            sent_count = 0
            failed_count = 0
            total = len(recipients)
            
            progress_msg = bot.send_message(chat_id, f"📤 <b>НАЧАЛАСЬ РАССЫЛКА...</b>\n\nОтправка сообщения {recipient_type}\nВсего получателей: {total}\nОтправлено: 0/{total}", parse_mode='HTML')
            
            for i, recipient_id in enumerate(recipients, 1):
                try:
                    if message.photo:
                        # Если это фото с подписью
                        bot.send_photo(
                            recipient_id,
                            message.photo[-1].file_id,
                            caption=message_text,
                            parse_mode=parse_mode
                        )
                    elif message.document:
                        # Если это документ
                        bot.send_document(
                            recipient_id,
                            message.document.file_id,
                            caption=message_text,
                            parse_mode=parse_mode
                        )
                    else:
                        # Если это просто текст
                        bot.send_message(
                            recipient_id,
                            message_text,
                            parse_mode=parse_mode
                        )
                    sent_count += 1
                    
                    # Обновляем прогресс каждые 10 сообщений
                    if i % 10 == 0 or i == total:
                        try:
                            bot.edit_message_text(
                                f"📤 <b>РАССЫЛКА В ПРОЦЕССЕ...</b>\n\nОтправка сообщения {recipient_type}\nВсего получателей: {total}\nОтправлено: {i}/{total}\nУспешно: {sent_count}\nНеудачно: {failed_count}",
                                chat_id,
                                progress_msg.message_id,
                                parse_mode='HTML'
                            )
                        except:
                            pass
                    
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Ошибка отправки пользователю {recipient_id}: {e}")
            
            # Завершаем рассылку
            del awaiting_broadcast_message[user_id]
            
            # Логируем рассылку
            log_activity(user_id, f'Отправил рассылку {recipient_type}', details=f'Тип: {broadcast_type}, Отправлено: {sent_count}, Неудачно: {failed_count}')
            
            result_text = f"""
✅ <b>РАССЫЛКА ЗАВЕРШЕНА</b>

<b>Тип рассылки:</b> {recipient_type}
<b>Всего получателей:</b> {total}
<b>Успешно отправлено:</b> {sent_count}
<b>Не удалось отправить:</b> {failed_count}

<b>Рассылка выполнена успешно!</b>
            """
            
            try:
                bot.delete_message(chat_id, progress_msg.message_id)
            except:
                pass
            
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("📢 Новая рассылка", callback_data='broadcast_menu'))
            keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
            
            send_photo_message(chat_id, None, result_text, keyboard)
            return
        
        # Обработка личных сообщений
        elif user_id in awaiting_private_message:
            recipient_info = awaiting_private_message[user_id]
            
            if message.text and message.text.strip() == '/cancel':
                del awaiting_private_message[user_id]
                send_photo_message(chat_id, None, "❌ <b>ОТПРАВКА СООБЩЕНИЯ ОТМЕНЕНА</b>", private_message_menu_keyboard())
                return
            
            # Если recipient_info - это True, значит нужно распарсить ID и сообщение из текста
            if recipient_info is True:
                parts = message.text.strip().split(' ', 1)
                if len(parts) < 2:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nИспользуйте: <code>ID_пользователя Ваше сообщение</code>", parse_mode='HTML')
                    return
                
                # Проверяем, является ли первый элемент числом (ID)
                if not parts[0].isdigit():
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nID пользователя должен быть числом", parse_mode='HTML')
                    return
                
                try:
                    recipient_id = int(parts[0])
                    message_text = parts[1]
                except ValueError:
                    bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nID пользователя должен быть числом", parse_mode='HTML')
                    return
            else:
                # Если recipient_info - это ID пользователя
                recipient_id = recipient_info
                message_text = message.text or message.caption or ""
            
            # Проверяем, существует ли пользователь
            if recipient_id not in users:
                bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН</b>\n\nПользователь с ID {recipient_id} не зарегистрирован в системе.", parse_mode='HTML')
                del awaiting_private_message[user_id]
                return
            
            recipient = users[recipient_id]
            parse_mode = 'HTML'
            
            # Отправляем сообщение
            try:
                if message.photo:
                    # Если это фото с подписью
                    bot.send_photo(
                        recipient_id,
                        message.photo[-1].file_id,
                        caption=message_text,
                        parse_mode=parse_mode
                    )
                elif message.document:
                    # Если это документ
                    bot.send_document(
                        recipient_id,
                        message.document.file_id,
                        caption=message_text,
                        parse_mode=parse_mode
                    )
                else:
                    # Если это просто текст
                    bot.send_message(
                        recipient_id,
                        message_text,
                        parse_mode=parse_mode
                    )
                
                # Логируем отправку личного сообщения
                log_activity(user_id, f'Отправил личное сообщение пользователю ID:{recipient_id}')
                
                result_text = f"""
✅ <b>СООБЩЕНИЕ ОТПРАВЛЕНО</b>

<b>Получатель:</b> @{recipient['username']}
<b>ID:</b> <code>{recipient_id}</code>

<b>Сообщение успешно доставлено!</b>
                """
                
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton("✉️ Новое сообщение", callback_data='private_message'))
                keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
                
                send_photo_message(chat_id, None, result_text, keyboard)
                
            except Exception as e:
                error_text = f"""
❌ <b>ОШИБКА ОТПРАВКИ</b>

<b>Получатель:</b> @{recipient['username']}
<b>ID:</b> <code>{recipient_id}</code>

<b>Не удалось отправить сообщение:</b>
{str(e)}

<b>Возможно, пользователь заблокировал бота.</b>
                """
                
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton("🔄 Попробовать снова", callback_data=f'admin_message_user_{recipient_id}'))
                keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
                
                send_photo_message(chat_id, None, error_text, keyboard)
            
            del awaiting_private_message[user_id]
            return
        
        # НОВЫЕ ФУНКЦИИ: Обработка блокировок пользователей
        elif user.get('awaiting_block_user'):
            if user_id not in owners:
                bot.send_message(chat_id, "❌ <b>ДОСТУП ЗАПРЕЩЁН</b>\n\nТолько владельцы могут блокировать пользователей.", parse_mode='HTML')
                users[user_id]['awaiting_block_user'] = False
                return
            
            try:
                target_user_id = int(message.text)
                
                if target_user_id in blocked_users:
                    bot.send_message(chat_id, f"⚠️ <b>ПОЛЬЗОВАТЕЛЬ УЖЕ ЗАБЛОКИРОВАН</b>\n\nПользователь {target_user_id} уже находится в списке заблокированных.", parse_mode='HTML')
                    users[user_id]['awaiting_block_user'] = False
                    return
                
                # Блокируем пользователя
                blocked_users.add(target_user_id)
                save_data()
                
                # Логируем блокировку
                log_activity(user_id, f'Заблокировал пользователя ID:{target_user_id}')
                
                # Отправляем уведомление пользователю
                if target_user_id in users:
                    user_name = users[target_user_id]['username']
                    block_notification = f"""
🚫 <b>ВЫ БЫЛИ ЗАБЛОКИРОВАНЫ</b>

Ваш аккаунт был заблокирован владельцем системы.
Вы потеряли доступ ко всем функциям бота.

<b>Причина блокировки:</b> Нарушение правил системы
<b>Заблокировал:</b> Владелец системы
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

Для выяснения причин и возможной разблокировки обратитесь к владельцу.
                    """
                    try:
                        bot.send_message(target_user_id, block_notification, parse_mode='HTML')
                    except:
                        pass
                
                result_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН</b>

<b>Пользователь:</b> @{user_name if target_user_id in users else target_user_id}
<b>ID:</b> <code>{target_user_id}</code>
<b>Заблокировал:</b> @{user['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь полностью потерял доступ к боту.</b>
<i>Уведомление отправлено пользователю.</i>
                """
                
                send_photo_message(chat_id, None, result_text, block_user_menu_keyboard())
                users[user_id]['awaiting_block_user'] = False
                return
            except ValueError:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nВведите целое число", parse_mode='HTML')
                return
        
        elif user.get('awaiting_unblock_user'):
            if user_id not in owners:
                bot.send_message(chat_id, "❌ <b>ДОСТУП ЗАПРЕЩЁН</b>\n\nТолько владельцы могут разблокировать пользователей.", parse_mode='HTML')
                users[user_id]['awaiting_unblock_user'] = False
                return
            
            try:
                target_user_id = int(message.text)
                
                if target_user_id not in blocked_users:
                    bot.send_message(chat_id, f"⚠️ <b>ПОЛЬЗОВАТЕЛЬ НЕ ЗАБЛОКИРОВАН</b>\n\nПользователь {target_user_id} не находится в списке заблокированных.", parse_mode='HTML')
                    users[user_id]['awaiting_unblock_user'] = False
                    return
                
                # Разблокируем пользователя
                blocked_users.remove(target_user_id)
                save_data()
                
                # Логируем разблокировку
                log_activity(user_id, f'Разблокировал пользователя ID:{target_user_id}')
                
                # Отправляем уведомление пользователю
                if target_user_id in users:
                    user_name = users[target_user_id]['username']
                    unblock_notification = f"""
✅ <b>ВЫ БЫЛИ РАЗБЛОКИРОВАНЫ</b>

Ваш аккаунт был разблокирован владельцем системы.
Доступ ко всем функциям бота восстановлен.

<b>Разблокировал:</b> Владелец системы
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Ваш уровень доступа:</b>
"""
                    # Добавляем информацию об уровне пользователя
                    if target_user_id in owners:
                        unblock_notification += "👑 Владелец"
                    elif target_user_id in admins:
                        unblock_notification += "⚙️ Администратор"
                    elif target_user_id in workers:
                        unblock_notification += "👷 Воркер"
                    else:
                        unblock_notification += "👤 Пользователь"
                    
                    unblock_notification += "\n\nДобро пожаловать обратно в систему!"
                    
                    try:
                        bot.send_message(target_user_id, unblock_notification, parse_mode='HTML')
                    except:
                        pass
                
                result_text = f"""
✅ <b>ПОЛЬЗОВАТЕЛЬ РАЗБЛОКИРОВАН</b>

<b>Пользователь:</b> @{user_name if target_user_id in users else target_user_id}
<b>ID:</b> <code>{target_user_id}</code>
<b>Разблокировал:</b> @{user['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Доступ пользователя к боту восстановлен.</b>
<i>Уведомление отправлено пользователю.</i>
                """
                
                send_photo_message(chat_id, None, result_text, block_user_menu_keyboard())
                users[user_id]['awaiting_unblock_user'] = False
                return
            except ValueError:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nВведите целое число", parse_mode='HTML')
                return
    
    # Обработка установки реквизитов (для всех пользователей)
    if user.get('awaiting_ton_wallet'):
        users[user_id]['ton_wallet'] = message.text
        users[user_id]['awaiting_ton_wallet'] = False
        save_data()
        
        # Логируем обновление реквизитов
        log_activity(user_id, 'Обновил TON кошелёк', details=f'Новый адрес: {message.text[:20]}...')
        
        notify_admin_credentials(user_id, 'ton_wallet', message.text)
        
        wallet_updated_text = f"""
✅ <b>TON КОШЕЛЁК ОБНОВЛЁН</b>

<b>Новый адрес:</b>
<code>{message.text}</code>

<b>Теперь вы можете получать Ton платежи на этот кошелёк.</b>
<i>Всегда проверяйте правильность адреса перед публикацией сделки.</i>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🏦 Все реквизиты", callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, None, wallet_updated_text, keyboard)
        return
    
    elif user.get('awaiting_card_details'):
        users[user_id]['card_details'] = message.text
        users[user_id]['awaiting_card_details'] = False
        save_data()
        
        # Логируем обновление реквизитов
        log_activity(user_id, 'Обновил банковскую карту', details=f'Новые реквизиты: {message.text[:20]}...')
        
        notify_admin_credentials(user_id, 'card_details', message.text)
        
        card_updated_text = f"""
✅ <b>БАНКОВСКАЯ КАРТА ОБНОВЛЕНА</b>

<b>Новые реквизиты:</b>
<code>{message.text}</code>

<b>Теперь вы можете получать рублёвые платежи на эту карту.</b>
<i>Реквизиты будут автоматически показаны покупателям.</i>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🏦 Все реквизиты", callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, None, card_updated_text, keyboard)
        return
    
    elif user.get('awaiting_phone'):
        users[user_id]['phone_number'] = message.text
        users[user_id]['awaiting_phone'] = False
        save_data()
        
        # Логируем обновление реквизитов
        log_activity(user_id, 'Обновил номер телефона', details=f'Новый номер: {message.text}')
        
        phone_updated_text = f"""
✅ <b>НОМЕР ТЕЛЕФОНА ОБНОВЛЁН</b>

<b>Новый номер:</b>
<code>{message.text}</code>

<b>Теперь вы можете получать платежи Qiwi/юmoney на этот номер.</b>
<i>Убедитесь, что номер активен и привязан к кошельку.</i>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🏦 Все реквизиты", callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, None, phone_updated_text, keyboard)
        return
    
    elif user.get('awaiting_usdt'):
        users[user_id]['usdt_wallet'] = message.text
        users[user_id]['awaiting_usdt'] = False
        save_data()
        
        # Логируем обновление реквизитов
        log_activity(user_id, 'Обновил USDT кошелёк', details=f'Новый адрес: {message.text[:20]}...')
        
        usdt_updated_text = f"""
✅ <b>USDT КОШЕЛЁК ОБНОВЛЁН</b>

<b>Новый адрес (TRC20):</b>
<code>{message.text}</code>

<b>Теперь вы можете получать Usdt платежи на этот кошелёк.</b>
<i>Проверьте, что адрес принадлежит сети TRC20.</i>
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🏦 Все реквизиты", callback_data='wallet_menu'))
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        send_photo_message(chat_id, None, usdt_updated_text, keyboard)
        return
    
    elif user.get('awaiting_deal_amount'):
        try:
            amount = float(message.text)
            if amount <= 0:
                bot.send_message(chat_id, "❌ <b>СУММА ДОЛЖНА БЫТЬ БОЛЬШЕ НУЛЯ</b>", parse_mode='HTML')
                return
            
            users[user_id]['current_deal']['amount'] = amount
            users[user_id]['awaiting_deal_amount'] = False
            
            category_text = """
📁 <b>ВЫБЕРИТЕ КАТЕГОРИЮ ТОВАРА</b>

<b>Доступные категории:</b>
• 🎁 Подарок — цифровые подарки, стикеры
• 🏷️ Nft тег — Nft метки, коллекции
• 📢 Канал/чат — Telegram каналы, чаты
• ⭐ Stars — игровая валюта, бонусы

<b>Выберите категорию:</b>
            """
            send_photo_message(chat_id, None, category_text, product_category_keyboard())
        except ValueError:
            bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ СУММЫ</b>\n\nВведите число, например: 1500 или 5.75", parse_mode='HTML')
        return
    
    elif user.get('awaiting_deal_category'):
        description = message.text
        
        if len(description) < 10:
            bot.send_message(chat_id, "❌ <b>ОПИСАНИЕ СЛИШКОМ КОРОТКОЕ</b>\n\nМинимум 10 символов", parse_mode='HTML')
            return
        
        deal_id = str(uuid.uuid4())
        deal_data = users[user_id]['current_deal']
        deal_data['description'] = description
        deal_data['status'] = 'created'
        deal_data['created_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        deal_data['deal_id'] = deal_id
        
        deals[deal_id] = deal_data
        
        users[user_id]['awaiting_deal_category'] = False
        users[user_id]['current_deal'] = None
        save_data()
        
        # Логируем создание сделки
        log_activity(user_id, 'Создал новую сделку', deal_id, f'Сумма: {deal_data["amount"]} {deal_data["currency"]}, Категория: {deal_data.get("category", "Товар")}')
        
        deal_text = f"""
✅ <b>СДЕЛКА СОЗДАНА!</b>

📋 <b>ID сделки:</b> #{deal_id[:8]}
💰 <b>Сумма:</b> {deal_data['amount']} {deal_data['currency']}
📁 <b>Категория:</b> {deal_data.get('category', 'Товар')}
📝 <b>Описание:</b> {description}
👤 <b>Продавец:</b> @{user['username']}

<b>Ссылка для покупателя:</b>
https://t.me/{bot.get_me().username}?start={deal_id}

<b>Отправьте эту ссылку покупателю:</b>
https://t.me/{bot.get_me().username}?start={deal_id}

<i>Как только покупатель перейдёт по ссылке, сделка начнётся.</i>
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("📋 Мои сделки", callback_data='my_deals'),
            InlineKeyboardButton("🔙 В меню", callback_data='main_menu')
        )
        
        send_photo_message(chat_id, None, deal_text, keyboard)
        return
    
    # Обработка команд администратора/владельца
    if user_id in admins or user_id in owners:
        if user.get('awaiting_admin_id'):
            try:
                new_admin_id = int(message.text)
                admins.add(new_admin_id)
                save_data()
                
                # Логируем добавление администратора
                log_activity(user_id, f'Добавил администратора ID:{new_admin_id}')
                
                admin_granted_text = f"""
👑 <b>АДМИНИСТРАТОР ДОБАВЛЕН</b>

<b>ID:</b> {new_admin_id}
<b>Добавил:</b> @{user['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь получил права администратора.</b>
                """
                send_photo_message(chat_id, None, admin_granted_text, admin_panel_menu(user_id))
                user['awaiting_admin_id'] = False
                return
            except ValueError:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nВведите целое число", parse_mode='HTML')
                return
        
        elif user.get('awaiting_worker_id'):
            try:
                new_worker_id = int(message.text)
                workers.add(new_worker_id)
                save_data()
                
                # Логируем добавление воркера
                log_activity(user_id, f'Добавил воркера ID:{new_worker_id}')
                
                if new_worker_id in users:
                    worker_name = users[new_worker_id]['username']
                    notification_text = f"""
👷 <b>ПОЗДРАВЛЯЕМ! ВЫ СТАЛИ ВОРКЕРОМ!</b>

Вам были выданы права воркера в системе Playerok OTC.

<b>Ваши новые возможности:</b>
• Доступ к воркер панели
• Возможность накрутки сделок (до 10 за раз)
• Возможность накрутки баланса (до 1000 в любой валюте, включая TON)
• Просмотр статистики
• Возможность оплаты сделок
• Установка тега для профитов

<b>Обязанности:</b>
• Соблюдение правил системы
• Честное ведение сделок
• Помощь пользователям при необходимости

Добро пожаловать в команду! 🎉
                    """
                    try:
                        bot.send_message(new_worker_id, notification_text, parse_mode='HTML')
                        log_activity(new_worker_id, 'Получил права воркера от администратора')
                    except:
                        pass
                
                worker_granted_text = f"""
👷 <b>ВОРКЕР ДОБАВЛЕН</b>

<b>ID:</b> {new_worker_id}
<b>Имя:</b> @{worker_name if new_worker_id in users else 'Неизвестно'}
<b>Добавил:</b> @{user['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Пользователь получил права воркера.</b>
<i>Уведомление отправлено новому воркеру.</i>
                """
                send_photo_message(chat_id, None, worker_granted_text, admin_panel_menu(user_id))
                user['awaiting_worker_id'] = False
                return
            except ValueError:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nВведите целое число", parse_mode='HTML')
                return
        
        elif user.get('awaiting_remove_worker'):
            try:
                target_id = int(message.text)
                
                # Проверяем, является ли это ID админа (только для владельцев
                if target_id in admins and user_id in owners:
                    # Это удаление админа
                    if target_id in owners:
                        bot.send_message(chat_id, "❌ <b>НЕЛЬЗЯ УДАЛИТЬ ВЛАДЕЛЬЦА</b>", parse_mode='HTML')
                        user['awaiting_remove_worker'] = False
                        return
                    
                    admins.remove(target_id)
                    save_data()
                    
                    # Логируем удаление администратора
                    log_activity(user_id, f'Удалил администратора ID:{target_id}')
                    
                    if target_id in users:
                        admin_name = users[target_id]['username']
                        notification_text = f"""
⚙️ <b>ВЫ БЫЛИ ЛИШЕНЫ СТАТУСА АДМИНИСТРАТОРА</b>

Ваш статус администратора был отозван владельцем.
Теперь вы являетесь обычным пользователем.

Если это ошибка, свяжитесь с владельцем.
                        """
                        try:
                            bot.send_message(target_id, notification_text, parse_mode='HTML')
                        except:
                            pass
                    
                    result_text = f"""
🗑️ <b>АДМИНИСТРАТОР УДАЛЁН</b>

<b>Администратор:</b> @{admin_name if target_id in users else target_id}
<b>ID:</b> <code>{target_id}</code>
<b>Удалил:</b> @{user['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус администратора успешно отозван.</b>
                    """
                elif target_id in workers:
                    # Это удаление воркера
                    workers.remove(target_id)
                    save_data()
                    
                    # Логируем удаление воркера
                    log_activity(user_id, f'Удалил воркера ID:{target_id}')
                    
                    if target_id in users:
                        worker_name = users[target_id]['username']
                        notification_text = f"""
❌ <b>ВЫ БЫЛИ ЛИШЕНЫ СТАТУСА ВОРКЕРА</b>

Ваш статус воркера был отозван администратором.
Теперь вы являетесь обычным пользователем.

Если это ошибка, свяжитесь с поддержкой.
                        """
                        try:
                            bot.send_message(target_id, notification_text, parse_mode='HTML')
                        except:
                            pass
                    
                    result_text = f"""
✅ <b>ВОРКЕР УДАЛЁН</b>

<b>Воркер:</b> @{worker_name if target_id in users else target_id}
<b>ID:</b> <code>{target_id}</code>
<b>Удалил:</b> @{user['username']}
<b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

<b>Статус воркера успешно отозван.</b>
                    """
                else:
                    bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ {target_id} НЕ ЯВЛЯЕТСЯ ВОРКЕРОМ ИЛИ АДМИНИСТРАТОРОМ</b>", parse_mode='HTML')
                    user['awaiting_remove_worker'] = False
                    return
                
                send_photo_message(chat_id, None, result_text, admin_panel_menu(user_id))
                user['awaiting_remove_worker'] = False
                return
            except ValueError:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nВведите целое число", parse_mode='HTML')
                return
        
        elif user.get('awaiting_check_deals'):
            try:
                worker_id = int(message.text)
                user_data = users.get(worker_id)
                if user_data:
                    check_text = f"""
🔍 <b>ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{user_data['username']}
<b>ID:</b> <code>{worker_id}</code>
<b>Роль:</b> {"👑 Владелец" if worker_id in owners else "⚙️ Админ" if worker_id in admins else "👷 Воркер" if worker_id in workers else "👤 Пользователь"}
<b>Статус блокировки:</b> {"🚫 Заблокирован" if is_user_blocked(worker_id) else "✅ Активен"}
<b>Сделок:</b> {user_data['success_deals']}
<b>Рейтинг:</b> {user_data['rating']}⭐
<b>Дата регистрации:</b> {user_data['join_date']}
                    """
                    
                    if worker_id in workers:
                        keyboard = InlineKeyboardMarkup(row_width=2)
                        keyboard.add(
                            InlineKeyboardButton("🗑️ Удалить воркера", callback_data=f'remove_worker_confirm_{worker_id}'),
                            InlineKeyboardButton("📉 Понизить", callback_data=f'demote_worker_confirm_{worker_id}')
                        )
                        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='show_workers'))
                    elif worker_id in admins and user_id in owners and worker_id not in owners:
                        keyboard = InlineKeyboardMarkup(row_width=2)
                        keyboard.add(
                            InlineKeyboardButton("🗑️ Удалить админа", callback_data=f'remove_admin_confirm_{worker_id}'),
                            InlineKeyboardButton("👤 Профиль", callback_data=f'admin_view_user_{worker_id}')
                        )
                        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='show_admins'))
                    else:
                        keyboard = InlineKeyboardMarkup(row_width=1)
                        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='show_workers' if worker_id in workers else 'show_admins' if worker_id in admins else 'admin_panel'))
                    
                    send_photo_message(chat_id, None, check_text, keyboard)
                else:
                    bot.send_message(chat_id, f"❌ <b>ПОЛЬЗОВАТЕЛЬ {worker_id} НЕ НАЙДЕН</b>", parse_mode='HTML')
                user['awaiting_check_deals'] = False
                return
            except ValueError:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID</b>\n\nВведите целое число", parse_mode='HTML')
                return
        
        elif user.get('awaiting_fake_deals'):
            try:
                if ' ' in message.text:
                    target_id, count = map(int, message.text.split())
                else:
                    target_id = user_id
                    count = int(message.text)
                
                if target_id not in users:
                    init_user(target_id)
                
                users[target_id]['success_deals'] += count
                save_data()
                
                # Логируем накрутку сделок
                log_activity(user_id, f'Накрутил сделки пользователю ID:{target_id}', details=f'Количество: {count}')
                
                fake_deals_done_text = f"""
💼 <b>СДЕЛКИ НАКРУЧЕНЫ</b>

<b>Пользователь:</b> {target_id}
<b>Добавлено сделок:</b> {count}
<b>Итого сделок:</b> {users[target_id]['success_deals']}
<b>Выполнил:</b> @{user['username']}

<b>Статистика пользователя обновлена.</b>
                """
                send_photo_message(chat_id, None, fake_deals_done_text, admin_panel_menu(user_id))
                user['awaiting_fake_deals'] = False
                return
            except:
                bot.send_message(chat_id, "❌ <b>ОШИБКА ФОРМАТА</b>\n\nИспользуйте: <code>12345678 15</code> или просто <code>15</code>", parse_mode='HTML')
                return
        
        elif user.get('awaiting_fake_balance'):
            try:
                parts = message.text.split()
                if len(parts) == 3:
                    target_id = int(parts[0])
                    amount = float(parts[1])
                    currency = parts[2].upper()
                elif len(parts) == 2:
                    target_id = user_id
                    amount = float(parts[0])
                    currency = parts[1].upper()
                else:
                    bot.send_message(chat_id, "❌ <b>НЕДОСТАТОЧНО ДАННЫХ</b>\n\nФормат: <code>12345678 100 Rub</code> или <code>100 Rub</code>", parse_mode='HTML')
                    return
                
                valid_currencies = ['TON', 'RUB', 'USD', 'KZT', 'UAH', 'BYN', 'USDT', 'STARS']
                if currency not in valid_currencies:
                    bot.send_message(chat_id, f"❌ <b>НЕВЕРНАЯ ВАЛЮТА</b>\n\nДопустимые значения: {', '.join(valid_currencies)}", parse_mode='HTML')
                    return
                
                if target_id not in users:
                    init_user(target_id)
                
                users[target_id]['balance'][currency] += amount
                save_data()
                
                # Логируем накрутку баланса
                log_activity(user_id, f'Накрутил баланс пользователю ID:{target_id}', details=f'Сумма: {amount} {currency}')
                
                fake_balance_done_text = f"""
💰 <b>БАЛАНС ПОПОЛНЕН</b>

<b>Пользователь:</b> {target_id}
<b>Валюта:</b> {currency}
<b>Сумма:</b> {amount}
<b>Итого баланс:</b> {users[target_id]['balance'][currency]} {currency}
<b>Выполнил:</b> @{user['username']}

<b>Баланс пользователя обновлён.</b>
                """
                send_photo_message(chat_id, None, fake_balance_done_text, admin_panel_menu(user_id))
                user['awaiting_fake_balance'] = False
                return
            except Exception as e:
                bot.send_message(chat_id, f"❌ <b>ОШИБКА ОБРАБОТКИ</b>\n\n{str(e)}", parse_mode='HTML')
                return
    
    # Обработка накрутки баланса для воркеров
    elif user.get('awaiting_fake_balance'):
        try:
            parts = message.text.split()
            if len(parts) == 2:
                amount = float(parts[0])
                currency = parts[1].upper()
                
                # Проверяем лимит для воркеров (1000 в любой валюте)
                if user_id in workers and amount > 1000:
                    bot.send_message(chat_id, "❌ <b>ПРЕВЫШЕН ЛИМИТ</b>\n\nВоркеры могут накручивать не более 1000 за раз", parse_mode='HTML')
                    user['awaiting_fake_balance'] = False
                    return
                
                valid_currencies = ['TON', 'RUB', 'USD', 'KZT', 'UAH', 'BYN', 'USDT', 'STARS']
                if currency not in valid_currencies:
                    bot.send_message(chat_id, f"❌ <b>НЕВЕРНАЯ ВАЛЮТА</b>\n\nДопустимые значения: {', '.join(valid_currencies)}", parse_mode='HTML')
                    user['awaiting_fake_balance'] = False
                    return
                
                users[user_id]['balance'][currency] += amount
                save_data()
                
                # Логируем накрутку баланса
                log_activity(user_id, f'Накрутил баланс', details=f'Сумма: {amount} {currency}')
                
                fake_balance_done_text = f"""
💰 <b>БАЛАНС ПОПОЛНЕН</b>

<b>Валюта:</b> {currency}
<b>Сумма:</b> {amount}
<b>Итого баланс:</b> {users[user_id]['balance'][currency]} {currency}

<b>Баланс успешно пополнен.</b>
                """
                send_photo_message(chat_id, None, fake_balance_done_text, worker_panel_menu())
                user['awaiting_fake_balance'] = False
                return
            else:
                bot.send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ</b>\n\nИспользуйте: <code>100 Rub</code> или <code>50 Stars</code> или <code>10 Ton</code>", parse_mode='HTML')
                return
        except Exception as e:
            bot.send_message(chat_id, f"❌ <b>ОШИБКА ОБРАБОТКИ</b>\n\n{str(e)}", parse_mode='HTML')
            return
    
    # Обработка накрутки сделок для воркеров
    elif user.get('awaiting_fake_deals'):
        try:
            if ' ' in message.text:
                parts = message.text.split()
                if len(parts) == 2:
                    target_id = int(parts[0])
                    count = int(parts[1])
                    
                    # Воркеры могут накручивать только себе
                    if user_id in workers and target_id != user_id:
                        bot.send_message(chat_id, "❌ <b>ВОРКЕРЫ МОГУТ НАКРУЧИВАТЬ ТОЛЬКО СЕБЕ</b>", parse_mode='HTML')
                        user['awaiting_fake_deals'] = False
                        return
                    
                    if target_id not in users:
                        init_user(target_id)
                    
                    # Проверяем лимит для воркеров
                    if user_id in workers and count > 10:
                        bot.send_message(chat_id, "❌ <b>ПРЕВЫШЕН ЛИМИТ</b>\n\nВоркеры могут накручивать не более 10 сделок за раз", parse_mode='HTML')
                        user['awaiting_fake_deals'] = False
                        return
                    
                    users[target_id]['success_deals'] += count
                    save_data()
                    
                    # Логируем накрутку сделок
                    log_activity(user_id, f'Накрутил сделки пользователю ID:{target_id}', details=f'Количество: {count}')
                    
                    fake_deals_done_text = f"""
💼 <b>СДЕЛКИ НАКРУЧЕНЫ</b>

<b>Пользователь:</b> {target_id}
<b>Добавлено сделок:</b> {count}
<b>Итого сделок:</b> {users[target_id]['success_deals']}
<b>Выполнил:</b> @{user['username']}

<b>Статистика пользователя обновлена.</b>
                    """
                    
                    if user_id in workers:
                        send_photo_message(chat_id, None, fake_deals_done_text, worker_panel_menu())
                    else:
                        send_photo_message(chat_id, None, fake_deals_done_text, admin_panel_menu(user_id))
                    
                    user['awaiting_fake_deals'] = False
                    return
            else:
                # Если введено только число, накручиваем себе
                count = int(message.text)
                
                # Проверяем лимит для воркеров
                if user_id in workers and count > 10:
                    bot.send_message(chat_id, "❌ <b>ПРЕВЫШЕН ЛИМИТ</b>\n\nВоркеры могут накручивать не более 10 сделок за раз", parse_mode='HTML')
                    user['awaiting_fake_deals'] = False
                    return
                
                users[user_id]['success_deals'] += count
                save_data()
                
                # Логируем накрутку сделок
                log_activity(user_id, f'Накрутил сделки себе', details=f'Количество: {count}')
                
                fake_deals_done_text = f"""
💼 <b>СДЕЛКИ НАКРУЧЕНЫ</b>

<b>Добавлено сделок:</b> {count}
<b>Итого сделок:</b> {users[user_id]['success_deals']}

<b>Статистика обновлена.</b>
                """
                
                if user_id in workers:
                    send_photo_message(chat_id, None, fake_deals_done_text, worker_panel_menu())
                else:
                    send_photo_message(chat_id, None, fake_deals_done_text, admin_panel_menu(user_id))
                
                user['awaiting_fake_deals'] = False
                return
        except Exception as e:
            bot.send_message(chat_id, f"❌ <b>ОШИБКА ОБРАБОТКИ</b>\n\n{str(e)}", parse_mode='HTML')
            return

# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот Playerok OTC запущен!")
    print("🔄 Ожидание сообщений...")
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        print("🔄 Перезапуск через 5 секунд...")
        time.sleep(5)
