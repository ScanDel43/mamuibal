from bot_core import *

# Генерация клавиатуры главного меню с большими кнопками
def main_menu(user_id):
    update_user_activity(user_id)
    
    # Проверяем блокировку
    if is_user_blocked(user_id):
        blocked_text = """
🚫 <b>ВЫ ЗАБЛОКИРОВАНЫ</b>

Ваш аккаунт был заблокирован администрацией.
Вы не можете использовать функционал бота.

Для выяснения причин обратитесь к администратору.
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📞 Связь с администрацией", url='https://t.me/RelayerPlayerok'))
        return blocked_text, keyboard
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Добавляем кнопку админ-панели только для админов
    if user_id in owners:
        keyboard.add(
            InlineKeyboardButton("👤 Мой профиль", callback_data='my_profile'),
            InlineKeyboardButton("💼 Мои сделки", callback_data='my_deals')
        )
        keyboard.add(
            InlineKeyboardButton("⚡ Создать сделку", callback_data='warning_show'),
            InlineKeyboardButton("🏦 Реквизиты", callback_data='wallet_menu')
        )
        keyboard.add(
            InlineKeyboardButton("🎯 Рефералы", callback_data='referral'),
            InlineKeyboardButton("🏷️ Мой тег", callback_data='my_tag')
        )
        keyboard.add(
            InlineKeyboardButton("👷 Воркер панель", callback_data='worker_panel'),
            InlineKeyboardButton("⚙️ Админ панель", callback_data='admin_panel')
        )
        keyboard.add(InlineKeyboardButton("📞 Поддержка", url='https://t.me/RelayerPlayerok'))
    elif user_id in admins:
        keyboard.add(
            InlineKeyboardButton("👤 Мой профиль", callback_data='my_profile'),
            InlineKeyboardButton("💼 Мои сделки", callback_data='my_deals')
        )
        keyboard.add(
            InlineKeyboardButton("⚡ Создать сделку", callback_data='warning_show'),
            InlineKeyboardButton("🏦 Реквизиты", callback_data='wallet_menu')
        )
        keyboard.add(
            InlineKeyboardButton("🎯 Рефералы", callback_data='referral'),
            InlineKeyboardButton("🏷️ Мой тег", callback_data='my_tag')
        )
        keyboard.add(
            InlineKeyboardButton("👷 Воркер панель", callback_data='worker_panel'),
            InlineKeyboardButton("⚙️ Админ панель", callback_data='admin_panel')
        )
        keyboard.add(InlineKeyboardButton("📞 Поддержка", url='https://t.me/RelayerPlayerok'))
    elif user_id in workers:
        keyboard.add(
            InlineKeyboardButton("👤 Мой профиль", callback_data='my_profile'),
            InlineKeyboardButton("💼 Мои сделки", callback_data='my_deals')
        )
        keyboard.add(
            InlineKeyboardButton("⚡ Создать сделку", callback_data='warning_show'),
            InlineKeyboardButton("🏦 Реквизиты", callback_data='wallet_menu')
        )
        keyboard.add(
            InlineKeyboardButton("🎯 Рефералы", callback_data='referral'),
            InlineKeyboardButton("🏷️ Мой тег", callback_data='my_tag')
        )
        keyboard.add(
            InlineKeyboardButton("👷 Воркер панель", callback_data='worker_panel'),
            InlineKeyboardButton("💱 Валюта", callback_data='change_currency')
        )
        keyboard.add(InlineKeyboardButton("📞 Поддержка", url='https://t.me/RelayerPlayerok'))
    else:
        keyboard.add(
            InlineKeyboardButton("👤 Мой профиль", callback_data='my_profile'),
            InlineKeyboardButton("💼 Мои сделки", callback_data='my_deals')
        )
        keyboard.add(
            InlineKeyboardButton("⚡ Создать сделку", callback_data='warning_show'),
            InlineKeyboardButton("🏦 Реквизиты", callback_data='wallet_menu')
        )
        keyboard.add(
            InlineKeyboardButton("🎯 Рефералы", callback_data='referral'),
            InlineKeyboardButton("💱 Валюта", callback_data='change_currency')
        )
        keyboard.add(InlineKeyboardButton("📞 Поддержка", url='https://t.me/RelayerPlayerok'))
    return get_welcome_text(), keyboard

# НОВОЕ МЕНЮ: Предупреждение перед созданием сделки
def warning_menu():
    warning_text = get_warning_menu()
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🤝 Только менеджеру", callback_data='confirm_manager'),
        InlineKeyboardButton("👤 Покупателю", callback_data='wrong_buyer')
    )
    keyboard.add(InlineKeyboardButton("🔙 Отмена", callback_data='main_menu'))
    
    return warning_text, keyboard

# Меню управления тегом
def tag_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🏷️ Установить тег", callback_data='set_tag'),
        InlineKeyboardButton("🗑️ Удалить тег", callback_data='remove_tag')
    )
    keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
    return keyboard

# Админ панель меню с большими кнопками
def admin_panel_menu(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📊 Статистика", callback_data='stats'),
        InlineKeyboardButton("👥 Пользователи", callback_data='show_users')
    )
    keyboard.add(
        InlineKeyboardButton("📋 Все сделки", callback_data='all_deals_admin'),
        InlineKeyboardButton("🔍 Действия в сделке", callback_data='deal_activities_admin')
    )
    keyboard.add(
        InlineKeyboardButton("👤 Действия пользователя", callback_data='user_activities_admin'),
        InlineKeyboardButton("📢 Рассылка", callback_data='broadcast_menu')
    )
    keyboard.add(
        InlineKeyboardButton("👷 Список воркеров", callback_data='show_workers'),
        InlineKeyboardButton("✉️ Личное сообщение", callback_data='private_message_menu')
    )
    keyboard.add(
        InlineKeyboardButton("👷 Выдать воркера", callback_data='add_worker'),
        InlineKeyboardButton("🗑️ Удалить воркера", callback_data='remove_worker')
    )
    keyboard.add(
        InlineKeyboardButton("🔍 Проверить сделки", callback_data='check_worker_deals'),
        InlineKeyboardButton("📉 Понизить воркера", callback_data='demote_worker')
    )
    keyboard.add(
        InlineKeyboardButton("💼 Накрутка сделок", callback_data='fake_deals'),
        InlineKeyboardButton("💰 Накрутка баланса", callback_data='fake_balance')
    )
    
    # Только владельцы могут добавлять/удалять админов и блокировать пользователей
    if user_id in owners:
        keyboard.add(
            InlineKeyboardButton("👑 Список админов", callback_data='show_admins'),
            InlineKeyboardButton("👑 Выдать админку", callback_data='add_admin')
        )
        keyboard.add(
            InlineKeyboardButton("🗑️ Удалить админа", callback_data='remove_admin'),
            InlineKeyboardButton("🚫 Блокировка", callback_data='block_user_menu')
        )
    
    keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
    return keyboard

# Меню управления блокировками
def block_user_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚫 Заблокировать", callback_data='block_user'),
        InlineKeyboardButton("✅ Разблокировать", callback_data='unblock_user')
    )
    keyboard.add(
        InlineKeyboardButton("📋 Список заблокированных", callback_data='blocked_users_list'),
        InlineKeyboardButton("🔙 В админку", callback_data='admin_panel')
    )
    return keyboard

# Меню списка заблокированных пользователей
def blocked_users_list_keyboard(page=0, users_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    all_blocked = list(blocked_users)
    if not all_blocked:
        keyboard.add(InlineKeyboardButton("📭 Нет заблокированных", callback_data='noop'))
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='block_user_menu'))
        return keyboard
    
    total_pages = (len(all_blocked) + users_per_page - 1) // users_per_page
    
    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page
    
    for blocked_id in all_blocked[start_idx:end_idx]:
        if blocked_id in users:
            user = users[blocked_id]
            keyboard.add(InlineKeyboardButton(f"🚫 @{user['username'][:15]}", callback_data=f'view_blocked_{blocked_id}'))
        else:
            keyboard.add(InlineKeyboardButton(f"🚫 ID:{blocked_id}", callback_data=f'view_blocked_{blocked_id}'))
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'blocked_list_{page-1}'))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'blocked_list_{page+1}'))
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='block_user_menu'))
    return keyboard

# Меню управления заблокированным пользователем
def blocked_user_management_menu(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Разблокировать", callback_data=f'unblock_user_{user_id}'),
        InlineKeyboardButton("👤 Профиль", callback_data=f'admin_view_user_{user_id}')
    )
    keyboard.add(InlineKeyboardButton("🔙 К списку", callback_data='blocked_users_list'))
    return keyboard

# Меню списка админов (только для владельцев)
def admins_list_menu(page=0, admins_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    all_admin_ids = list(admins)
    if not all_admin_ids:
        keyboard.add(InlineKeyboardButton("📭 Нет администраторов", callback_data='noop'))
        keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
        return keyboard
    
    total_pages = (len(all_admin_ids) + admins_per_page - 1) // admins_per_page
    
    start_idx = page * admins_per_page
    end_idx = start_idx + admins_per_page
    
    for admin_id in all_admin_ids[start_idx:end_idx]:
        if admin_id in owners:
            role_icon = "👑 Владелец"
        else:
            role_icon = "⚙️ Админ"
        
        user = users.get(admin_id, {'username': f'ID:{admin_id}'})
        keyboard.add(InlineKeyboardButton(f"{role_icon} @{user['username'][:15]}", callback_data=f'view_admin_{admin_id}'))
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'show_admins_{page-1}'))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'show_admins_{page+1}'))
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
    return keyboard

# Меню управления админом (только для владельцев)
def admin_management_menu(admin_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Не позволяем удалять владельцев
    if admin_id in owners:
        keyboard.add(InlineKeyboardButton("👑 Владелец (нельзя удалить)", callback_data='noop'))
    else:
        keyboard.add(
            InlineKeyboardButton("🗑️ Удалить админа", callback_data=f'remove_admin_confirm_{admin_id}'),
            InlineKeyboardButton("👤 Профиль", callback_data=f'admin_view_user_{admin_id}')
        )
    
    keyboard.add(InlineKeyboardButton("🔙 К списку", callback_data='show_admins'))
    return keyboard

# Меню рассылок
def broadcast_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📢 Всем пользователям", callback_data='broadcast_all'),
        InlineKeyboardButton("👷 Только воркерам", callback_data='broadcast_workers')
    )
    keyboard.add(
        InlineKeyboardButton("👑 Только админам", callback_data='broadcast_admins'),
        InlineKeyboardButton("👤 Конкретному пользователю", callback_data='private_message')
    )
    keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
    return keyboard

# Меню личных сообщений
def private_message_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✉️ Написать пользователю", callback_data='private_message'),
        InlineKeyboardButton("📋 Список получателей", callback_data='private_message_list')
    )
    keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
    return keyboard

# Воркер панель меню с большими кнопки
def worker_panel_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Моя статистика", callback_data='worker_stats'),
        InlineKeyboardButton("📋 Мои сделки", callback_data='my_deals')
    )
    keyboard.add(
        InlineKeyboardButton("💼 Накрутка сделок", callback_data='worker_fake_deals'),
        InlineKeyboardButton("💰 Накрутка баланса", callback_data='worker_fake_balance')
    )
    keyboard.add(
        InlineKeyboardButton("🏷️ Мой тег", callback_data='my_tag'),
        InlineKeyboardButton("🔙 В меню", callback_data='main_menu')
    )
    return keyboard

# Меню управления воркером с большими кнопки
def worker_management_menu(worker_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🗑️ Удалить воркера", callback_data=f'remove_worker_confirm_{worker_id}'),
        InlineKeyboardButton("📉 Понизить", callback_data=f'demote_worker_confirm_{worker_id}')
    )
    keyboard.add(
        InlineKeyboardButton("🔍 Проверить сделки", callback_data=f'check_worker_deals_{worker_id}'),
        InlineKeyboardButton("📊 Статистика", callback_data=f'worker_stats_{worker_id}')
    )
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='show_workers'))
    return keyboard

# Меню выбора валюты с большими кнопки (добавлена валюта Stars)
def currency_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🇷🇺 Rub", callback_data='currency_RUB'),
        InlineKeyboardButton("🇺🇸 Usd", callback_data='currency_USD')
    )
    keyboard.add(
        InlineKeyboardButton("🇰🇿 Kzt", callback_data='currency_KZT'),
        InlineKeyboardButton("🇺🇦 Uah", callback_data='currency_UAH')
    )
    keyboard.add(
        InlineKeyboardButton("🇧🇾 Byn", callback_data='currency_BYN'),
        InlineKeyboardButton("⚡ Ton", callback_data='currency_TON')
    )
    keyboard.add(
        InlineKeyboardButton("💎 Usdt", callback_data='currency_USDT'),
        InlineKeyboardButton("⭐ Stars", callback_data='currency_STARS')
    )
    keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
    return keyboard

# Меню реквизитов с большими кнопки (без Stars, так как Stars не требуют реквизитов)
def wallet_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⚡ Ton", callback_data='set_ton'),
        InlineKeyboardButton("💳 Карта", callback_data='set_card')
    )
    keyboard.add(
        InlineKeyboardButton("📱 Телефон", callback_data='set_phone'),
        InlineKeyboardButton("💎 Usdt", callback_data='set_usdt')
    )
    keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
    return keyboard

# Меню создания сделки с большими кнопки (добавлена валюта Stars)
def create_deal_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⚡ Ton", callback_data='method_TON'),
        InlineKeyboardButton("💎 Usdt", callback_data='method_USDT')
    )
    keyboard.add(
        InlineKeyboardButton("🇷🇺 Rub", callback_data='method_RUB'),
        InlineKeyboardButton("🇺🇸 Usd", callback_data='method_USD')
    )
    keyboard.add(
        InlineKeyboardButton("🇰🇿 Kzt", callback_data='method_KZT'),
        InlineKeyboardButton("🇺🇦 Uah", callback_data='method_UAH')
    )
    keyboard.add(
        InlineKeyboardButton("🇧🇾 Byn", callback_data='method_BYN'),
        InlineKeyboardButton("⭐ Stars", callback_data='method_STARS')
    )
    keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
    return keyboard

# Меню выбора категории товара с большими кнопки
def product_category_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎁 Подарок", callback_data='category_gift'),
        InlineKeyboardButton("🏷️ Nft тег", callback_data='category_nft')
    )
    keyboard.add(
        InlineKeyboardButton("📢 Канал/чат", callback_data='category_channel'),
        InlineKeyboardButton("⭐ Stars", callback_data='category_stars')
    )
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='create_deal'))
    return keyboard

# Меню сделки для продавца с большими кнопки
def deal_seller_keyboard(deal_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("⚠️ Открыть спор", callback_data=f'dispute_{deal_id}'))
    keyboard.add(InlineKeyboardButton("🔙 Мои сделки", callback_data='my_deals'))
    return keyboard

# Меню сделки для покупателя с большими кнопки
def deal_buyer_keyboard(deal_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💸 Оплатить с баланса", callback_data=f'pay_balance_{deal_id}'),
        InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f'confirm_pay_{deal_id}')
    )
    keyboard.add(InlineKeyboardButton("⚠️ Открыть спор", callback_data=f'dispute_{deal_id}'))
    keyboard.add(InlineKeyboardButton("🔙 Мои сделки", callback_data='my_deals'))
    return keyboard

# Меню для просмотра всех сделок админом
def all_deals_admin_keyboard(page=0, deals_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    all_deal_ids = list(deals.keys())
    total_pages = (len(all_deal_ids) + deals_per_page - 1) // deals_per_page
    
    start_idx = page * deals_per_page
    end_idx = start_idx + deals_per_page
    
    for deal_id in all_deal_ids[start_idx:end_idx]:
        deal = deals[deal_id]
        status_icon = "🟡" if deal.get('status') == 'created' else "🟢" if deal.get('status') == 'paid' else "🔵" if deal.get('status') == 'completed' else "🔴"
        keyboard.add(InlineKeyboardButton(f"{status_icon} #{deal_id[:8]}", callback_data=f'admin_view_deal_{deal_id}'))
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'all_deals_admin_{page-1}'))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'all_deals_admin_{page+1}'))
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    keyboard.add(InlineKeyboardButton("🔍 Поиск сделки", callback_data='search_deal_admin'))
    keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
    return keyboard

# Меню для выбора сделки для просмотра активности
def deal_activities_menu_keyboard(page=0, deals_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    all_deal_ids = list(deal_activities.keys())
    if not all_deal_ids:
        keyboard.add(InlineKeyboardButton("📭 Нет сделок с активностью", callback_data='noop'))
        keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
        return keyboard
    
    total_pages = (len(all_deal_ids) + deals_per_page - 1) // deals_per_page
    
    start_idx = page * deals_per_page
    end_idx = start_idx + deals_per_page
    
    for deal_id in all_deal_ids[start_idx:end_idx]:
        deal = deals.get(deal_id, {})
        activity_count = len(deal_activities.get(deal_id, []))
        status_icon = "🟡" if deal.get('status') == 'created' else "🟢" if deal.get('status') == 'paid' else "🔵" if deal.get('status') == 'completed' else "🔴" if deal else "⚫"
        keyboard.add(InlineKeyboardButton(f"{status_icon} #{deal_id[:8]} ({activity_count})", callback_data=f'admin_deal_activity_{deal_id}_0'))
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'deal_activities_menu_{page-1}'))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'deal_activities_menu_{page+1}'))
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    keyboard.add(InlineKeyboardButton("🔍 Поиск сделки", callback_data='search_deal_activity_admin'))
    keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
    return keyboard

# Меню для выбора пользователя для просмотра активности
def user_activities_menu_keyboard(page=0, users_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    all_user_ids = list(user_activities.keys())
    if not all_user_ids:
        keyboard.add(InlineKeyboardButton("📭 Нет пользователей с активностью", callback_data='noop'))
        keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
        return keyboard
    
    total_pages = (len(all_user_ids) + users_per_page - 1) // users_per_page
    
    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page
    
    for user_id in all_user_ids[start_idx:end_idx]:
        user = users.get(user_id, {})
        activity_count = len(user_activities.get(user_id, []))
        role_icon = "👑" if user_id in owners else "⚙️" if user_id in admins else "👷" if user_id in workers else "👤"
        username = user.get('username', str(user_id))
        keyboard.add(InlineKeyboardButton(f"{role_icon} @{username[:15]} ({activity_count})", callback_data=f'admin_user_activity_{user_id}_0'))
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'user_activities_menu_{page-1}'))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'user_activities_menu_{page+1}'))
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    keyboard.add(InlineKeyboardButton("🔍 Поиск пользователя", callback_data='search_user_activity_admin'))
    keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
    return keyboard

# Меню для выбора получателя личного сообщения
def private_message_recipients_keyboard(page=0, users_per_page=5):
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    all_user_ids = list(users.keys())
    if not all_user_ids:
        keyboard.add(InlineKeyboardButton("📭 Нет пользователей", callback_data='noop'))
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='private_message_menu'))
        return keyboard
    
    total_pages = (len(all_user_ids) + users_per_page - 1) // users_per_page
    
    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page
    
    for user_id in all_user_ids[start_idx:end_idx]:
        user = users.get(user_id, {})
        role_icon = "👑" if user_id in owners else "⚙️" if user_id in admins else "👷" if user_id in workers else "👤"
        username = user.get('username', str(user_id))
        keyboard.add(InlineKeyboardButton(f"{role_icon} @{username[:15]}", callback_data=f'select_recipient_{user_id}'))
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'private_message_list_{page-1}'))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'private_message_list_{page+1}'))
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    keyboard.add(InlineKeyboardButton("🔍 Поиск по ID", callback_data='search_recipient_admin'))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='private_message_menu'))
    return keyboard

# Функция для отображения профиля пользователя
def show_user_profile(user_id, chat_id, message_id=None):
    """Показывает профиль пользователя"""
    if user_id not in users:
        init_user(user_id)
    
    user = users[user_id]
    update_user_activity(user_id)
    
    role = "👤 Пользователь"
    if user_id in owners:
        role = "👑 Владелец"
    elif user_id in admins:
        role = "⚙️ Администратор"
    elif user_id in workers:
        role = "👷 Воркер"
    
    # Добавляем статус блокировки
    if is_user_blocked(user_id):
        role += " 🚫 (Заблокирован)"
    
    # Получаем тег пользователя
    user_tag = get_user_tag(user_id)
    
    active_deals = []
    for deal_id, deal in deals.items():
        if deal['seller_id'] == user_id or (deal.get('buyer_id') and deal['buyer_id'] == user_id):
            active_deals.append(deal_id)
    
    # Формируем текст профиля
    profile_text = f"🏆 <b>ПРОФИЛЬ PLAYEROK OTC</b>\n\n"
    profile_text += f"{role}\n"
    profile_text += f"👤 <b>Игрок:</b> @{user['username']}\n"
    profile_text += f"🏷️ <b>Тег:</b> {user_tag}\n"
    profile_text += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
    profile_text += f"📅 <b>В системе с:</b> {user['join_date']}\n"
    profile_text += f"⏰ <b>Последняя активность:</b> {user['last_active']}\n"
    profile_text += f"💱 <b>Основная валюта:</b> {user['currency']}\n\n"
    
    profile_text += f"⭐ <b>Рейтинг:</b> {user['rating']}/5.0\n"
    profile_text += f"✅ <b>Успешных сделок:</b> {user['success_deals']}\n"
    profile_text += f"⚖️ <b>Споров выиграно:</b> {user['disputes_won']}\n"
    profile_text += f"📊 <b>Активных сделок:</b> {len(active_deals)}\n\n"
    
    profile_text += f"💰 <b>Баланс:</b>\n"
    profile_text += f"• ⚡ Ton: <b>{user['balance']['TON']}</b>\n"
    profile_text += f"• 🇷🇺 Rub: <b>{user['balance']['RUB']}</b>\n"
    profile_text += f"• 🇺🇸 Usd: <b>{user['balance']['USD']}</b>\n"
    profile_text += f"• 🇰🇿 Kzt: <b>{user['balance']['KZT']}</b>\n"
    profile_text += f"• 🇺🇦 Uah: <b>{user['balance']['UAH']}</b>\n"
    profile_text += f"• 🇧🇾 Byn: <b>{user['balance']['BYN']}</b>\n"
    profile_text += f"• 💎 Usdt: <b>{user['balance']['USDT']}</b>\n"
    profile_text += f"• ⭐ Stars: <b>{user['balance']['STARS']}</b>\n\n"
    
    profile_text += f"🏦 <b>Реквизиты:</b>\n"
    profile_text += f"• Ton: <code>{user['ton_wallet']}</code>\n"
    profile_text += f"• Карта: <code>{user['card_details']}</code>\n"
    profile_text += f"• Телефон: <code>{user['phone_number']}</code>\n\n"
    
    profile_text += f"🔗 <b>Реферальная ссылка:</b>\n"
    profile_text += f"https://t.me/{bot.get_me().username}?start={user['referral_id']}\n\n"
    profile_text += f"<i>Приглашайте друзей и получайте бонусы!</i>"
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 Обновить", callback_data='my_profile'),
        InlineKeyboardButton("📝 Реквизиты", callback_data='wallet_menu')
    )
    keyboard.add(
        InlineKeyboardButton("📊 Статистика", callback_data='stats_public'),
        InlineKeyboardButton("🔙 В меню", callback_data='main_menu')
    )
    
    if message_id:
        send_photo_message(chat_id, message_id, profile_text, keyboard)
    else:
        send_photo_message(chat_id, None, profile_text, keyboard)

# Функция для отображения сделок пользователя
def show_user_deals(user_id, chat_id, message_id=None):
    """Показывает сделки пользователя"""
    if user_id not in users:
        init_user(user_id)
    
    user = users[user_id]
    update_user_activity(user_id)
    
    user_deals = []
    for deal_id, deal in deals.items():
        if deal['seller_id'] == user_id or (deal.get('buyer_id') and deal['buyer_id'] == user_id):
            user_deals.append((deal_id, deal))
    
    if not user_deals:
        deals_text = "📭 <b>У ВАС ПОКА НЕТ АКТИВНЫХ СДЕЛОК</b>\n\n"
        deals_text += "Создайте свою первую сделку с помощью кнопки ниже!"
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("⚡ Создать сделку", callback_data='warning_show'))
        keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
        
        if message_id:
            send_photo_message(chat_id, message_id, deals_text, keyboard)
        else:
            send_photo_message(chat_id, None, deals_text, keyboard)
        return
    
    deals_text = "📋 <b>ВАШИ АКТИВНЫЕ СДЕЛКИ</b>\n\n"
    
    for i, (deal_id, deal) in enumerate(user_deals[:5], 1):
        role = "🛒 Продавец" if deal['seller_id'] == user_id else "💰 Покупатель"
        status_icon = "🟡" if deal.get('status') == 'created' else "🟢" if deal.get('status') == 'paid' else "🔴"
        
        deals_text += f"{status_icon} <b>Сделка #{deal_id[:8]}</b>\n"
        deals_text += f"   {role}\n"
        deals_text += f"   💰 {deal['amount']} {deal['currency']}\n"
        deals_text += f"   📝 {deal.get('category', 'Товар')}: {deal['description'][:30]}...\n"
        
        if deal['seller_id'] == user_id:
            deals_text += f"   👤 Покупатель: "
            if deal.get('buyer_id'):
                buyer_tag = get_user_tag(deal['buyer_id'])
                deals_text += f"{buyer_tag}\n"
            else:
                deals_text += "Ожидается\n"
        else:
            seller_tag = get_user_tag(deal['seller_id'])
            deals_text += f"   👤 Продавец: {seller_tag}\n"
        
        deals_text += "   ───────────────\n"
    
    if len(user_deals) > 5:
        deals_text += f"\n📄 <i>И еще {len(user_deals) - 5} сделок...</i>\n"
    
    deals_text += "\nВыберите сделку для управления:"
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i, (deal_id, deal) in enumerate(user_deals[:3], 1):
        keyboard.add(InlineKeyboardButton(f"📄 Сделка #{deal_id[:8]}", callback_data=f'view_deal_{deal_id}'))
    
    if len(user_deals) > 3:
        keyboard.add(InlineKeyboardButton("📋 Все сделки", callback_data='all_deals'))
    
    keyboard.add(InlineKeyboardButton("⚡ Новая сделка", callback_data='warning_show'))
    keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
    
    if message_id:
        send_photo_message(chat_id, message_id, deals_text, keyboard)
    else:
        send_photo_message(chat_id, None, deals_text, keyboard)

# Функция для показа статистики обычным пользователям
def show_stats_public(user_id, chat_id, message_id=None):
    """Показывает статистику для обычных пользователей"""
    update_user_activity(user_id)
    
    total_users = len(users)
    
    stats_text = f"""
📊 <b>СТАТИСТИКА PLAYEROK OTC</b>

⭐ <b>Наша платформа активно развивается!</b>
<i>Присоединяйтесь к растущему сообществу</i>

💙 <b>Преимущества Playerok OTC:</b>
• 🔒 Гарант сделок
• ⚡ Быстрые выплаты
• 💎 Выгодные курсы
• 📞 Поддержка 24/7

🤍 <b>Мы растем вместе с вами!</b>
    """
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👤 Мой профиль", callback_data='my_profile'),
        InlineKeyboardButton("⚡ Создать сделку", callback_data='warning_show')
    )
    keyboard.add(InlineKeyboardButton("🔙 В меню", callback_data='main_menu'))
    
    if message_id:
        send_photo_message(chat_id, message_id, stats_text, keyboard)
    else:
        send_photo_message(chat_id, None, stats_text, keyboard)

# Функция для показа полной статистики админам
def show_stats_admin(user_id, chat_id, message_id=None):
    """Показывает полную статистику админам"""
    update_user_activity(user_id)
    
    active_users = sum(1 for u in users.values() if 
                      datetime.strptime(u['last_active'], "%d.%m.%Y %H:%M") > 
                      datetime.now().replace(hour=0, minute=0, second=0))
    
    online_now = 0
    five_minutes_ago = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=5)
    
    for u in users.values():
        try:
            last_active = datetime.strptime(u['last_active'], "%d.%m.%Y %H:%M")
            if last_active > five_minutes_ago:
                online_now += 1
        except:
            pass
    
    stats_text = f"""
📊 <b>СТАТИСТИКА PLAYEROK OTC (АДМИН)</b>

👥 <b>Пользователи:</b> {len(users)}
👑 <b>Владельцы:</b> {len(owners)}
⚙️ <b>Админы:</b> {len(admins) - len(owners)}
👷 <b>Воркеры:</b> {len(workers)}
🚫 <b>Заблокировано:</b> {len(blocked_users)}
📋 <b>Активных сделок:</b> {len(deals)}
👤 <b>Активных сегодня:</b> {active_users}
🟢 <b>Онлайн сейчас (~5 мин):</b> {online_now}

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
• Всего записей активности: {sum(len(v) for v in user_activities.values()) + sum(len(v) for v in deal_activities.values())}

<b>Теги пользователей:</b>
• Пользователей с тегами: {len(user_tags)}
• Воркеров с тегами: {len([uid for uid in workers if uid in user_tags])}
• Админов с тегами: {len([uid for uid in admins if uid in user_tags])}

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

# Функция для показа всех сделок админу
def show_all_deals_admin(user_id, chat_id, message_id=None, page=0):
    """Показывает все сделки в системе админу"""
    if user_id not in admins and user_id not in owners:
        return
    
    all_deal_ids = list(deals.keys())
    
    if not all_deal_ids:
        deals_text = "📭 <b>В СИСТЕМЕ НЕТ СДЕЛОК</b>\n\n"
        deals_text += "Пользователи еще не создали ни одной сделки."
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
        
        if message_id:
            send_photo_message(chat_id, message_id, deals_text, keyboard)
        else:
            send_photo_message(chat_id, None, deals_text, keyboard)
        return
    
    deals_per_page = 5
    total_pages = (len(all_deal_ids) + deals_per_page - 1) // deals_per_page
    start_idx = page * deals_per_page
    end_idx = start_idx + deals_per_page
    
    deals_text = f"📋 <b>ВСЕ СДЕЛКИ В СИСТЕМЕ</b>\n\n"
    deals_text += f"<b>Всего сделок:</b> {len(all_deal_ids)}\n"
    deals_text += f"<b>Страница:</b> {page + 1}/{total_pages}\n\n"
    
    for i, deal_id in enumerate(all_deal_ids[start_idx:end_idx], start_idx + 1):
        deal = deals[deal_id]
        
        status_map = {
            'created': '🟡 Создана',
            'paid': '🟢 Оплачена',
            'completed': '🔵 Завершена',
            'disputed': '🔴 Спор'
        }
        
        status = status_map.get(deal.get('status'), '⚫ Неизвестно')
        seller = users.get(deal['seller_id'], {'username': 'Неизвестно'})
        buyer = users.get(deal.get('buyer_id'), {'username': 'Не указан'})
        
        deals_text += f"<b>{i}. Сделка #{deal_id[:8]}</b>\n"
        deals_text += f"   Статус: {status}\n"
        deals_text += f"   Сумма: {deal['amount']} {deal['currency']}\n"
        deals_text += f"   Продавец: @{seller['username']}\n"
        deals_text += f"   Покупатель: @{buyer['username']}\n"
        deals_text += f"   Дата: {deal.get('created_at', 'Не указана')}\n"
        deals_text += f"   Категория: {deal.get('category', 'Товар')}\n"
        deals_text += "   ───────────────────\n"
    
    keyboard = all_deals_admin_keyboard(page)
    
    if message_id:
        send_photo_message(chat_id, message_id, deals_text, keyboard)
    else:
        send_photo_message(chat_id, None, deals_text, keyboard)

# Функция для показа деталей сделки админу
def show_deal_details_admin(user_id, chat_id, message_id, deal_id):
    """Показывает детали сделки админу"""
    if (user_id not in admins and user_id not in owners) or deal_id not in deals:
        return
    
    deal = deals[deal_id]
    seller = users.get(deal['seller_id'], {'username': 'Неизвестно', 'rating': 0, 'success_deals': 0})
    buyer = users.get(deal.get('buyer_id'), {'username': 'Неизвестно', 'rating': 0, 'success_deals': 0})
    
    status_map = {
        'created': '🟡 Создана',
        'paid': '🟢 Оплачена',
        'completed': '🔵 Завершена',
        'disputed': '🔴 Спор'
    }
    
    status = status_map.get(deal.get('status'), '⚫ Неизвестно')
    
    # Получаем теги участников
    seller_tag = get_user_tag(deal['seller_id'])
    buyer_tag = get_user_tag(deal.get('buyer_id')) if deal.get('buyer_id') else "Не указан"
    
    deal_text = f"""
🔍 <b>ДЕТАЛИ СДЕЛКИ (АДМИН)</b>

<b>ID сделки:</b> {deal_id}
<b>Статус:</b> {status}
<b>Создана:</b> {deal.get('created_at', 'Не указана')}

<b>💰 Сумма:</b> {deal['amount']} {deal['currency']}
<b>📁 Категория:</b> {deal.get('category', 'Товар')}
<b>📝 Описание:</b> {deal['description']}

<b>👤 Продавец:</b>
• Username: @{seller['username']}
• Тег: {seller_tag}
• ID: <code>{deal['seller_id']}</code>
• Рейтинг: {seller['rating']}⭐
• Сделок: {seller['success_deals']}

<b>👤 Покупатель:</b>
• Username: @{buyer['username']}
• Тег: {buyer_tag}
• ID: <code>{deal.get('buyer_id', 'Не указан')}</code>
• Рейтинг: {buyer['rating']}⭐
• Сделок: {buyer['success_deals']}

<b>🔗 Ссылка для покупателя:</b>
https://t.me/{bot.get_me().username}?start={deal_id}
    """
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Действия в сделке", callback_data=f'admin_deal_activity_{deal_id}_0'),
        InlineKeyboardButton("👤 Действия продавца", callback_data=f'admin_user_activity_{deal["seller_id"]}_0')
    )
    
    # Кнопка завершения сделки (только для оплаченных сделок)
    if deal.get('status') == 'paid':
        keyboard.add(
            InlineKeyboardButton("✅ Завершить сделку", callback_data=f'admin_complete_deal_{deal_id}'),
            InlineKeyboardButton("✉️ Написать продавцу", callback_data=f'admin_message_user_{deal["seller_id"]}')
        )
    else:
        if deal.get('buyer_id'):
            keyboard.add(
                InlineKeyboardButton("👤 Действия покупателя", callback_data=f'admin_user_activity_{deal["buyer_id"]}_0'),
                InlineKeyboardButton("✉️ Написать продавцу", callback_data=f'admin_message_user_{deal["seller_id"]}')
            )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Все сделки", callback_data='all_deals_admin'),
        InlineKeyboardButton("⚙️ В админку", callback_data='admin_panel')
    )
    
    send_photo_message(chat_id, message_id, deal_text, keyboard)

# Функция для показа активности в сделке
def show_deal_activities_admin(user_id, chat_id, message_id, deal_id, page=0):
    """Показывает активность в сделке админу"""
    if user_id not in admins and user_id not in owners:
        return
    
    activities = deal_activities.get(deal_id, [])
    deal = deals.get(deal_id, {})
    
    if not activities:
        activities_text = f"""
📊 <b>АКТИВНОСТЬ В СДЕЛКЕ</b>

<b>ID сделки:</b> #{deal_id[:8]}
<b>Статус:</b> {deal.get('status', 'Неизвестно')}
<b>Сумма:</b> {deal.get('amount', 0)} {deal.get('currency', '')}

<b>В этой сделке пока нет зафиксированных действий.</b>
        """
    else:
        activities_per_page = 5
        total_pages = (len(activities) + activities_per_page - 1) // activities_per_page
        start_idx = page * activities_per_page
        end_idx = start_idx + activities_per_page
        
        activities_text = f"""
📊 <b>АКТИВНОСТЬ В СДЕЛКЕ</b>

<b>ID сделки:</b> #{deal_id[:8]}
<b>Всего действий:</b> {len(activities)}
<b>Страница:</b> {page + 1}/{total_pages}

<b>Последние действия:</b>
"""
        
        for i, activity in enumerate(activities[start_idx:end_idx], start_idx + 1):
            user = users.get(activity['user_id'], {'username': f"ID:{activity['user_id']}"})
            user_tag = get_user_tag(activity['user_id'])
            details = f"\n   Подробности: {activity['details']}" if activity.get('details') else ""
            
            activities_text += f"""
{i}. <b>{activity['action']}</b>
   👤 Пользователь: {user_tag}
   ⏰ Время: {activity['timestamp']}{details}
   ───────────────────
"""
    
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # Навигация по страницам
    if len(activities) > 5:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'admin_deal_activity_{deal_id}_{page-1}'))
        
        nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
        
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'admin_deal_activity_{deal_id}_{page+1}'))
        
        if nav_buttons:
            keyboard.add(*nav_buttons)
    
    keyboard.add(
        InlineKeyboardButton("🔍 Детали сделки", callback_data=f'admin_view_deal_{deal_id}'),
        InlineKeyboardButton("📋 Все сделки", callback_data='all_deals_admin')
    )
    keyboard.add(InlineKeyboardButton("🔙 В админку", callback_data='admin_panel'))
    
    send_photo_message(chat_id, message_id, activities_text, keyboard)

# Функция для показа активности пользователя
def show_user_activities_admin(user_id, chat_id, message_id, target_user_id, page=0):
    """Показывает активность пользователя админу"""
    if user_id not in admins and user_id not in owners:
        return
    
    activities = user_activities.get(target_user_id, [])
    target_user = users.get(target_user_id, {'username': f"ID:{target_user_id}"})
    
    role = "👤 Пользователь"
    if target_user_id in owners:
        role = "👑 Владелец"
    elif target_user_id in admins:
        role = "⚙️ Администратор"
    elif target_user_id in workers:
        role = "👷 Воркер"
    
    # Добавляем статус блокировки
    if is_user_blocked(target_user_id):
        role += " 🚫 (Заблокирован)"
    
    # Получаем тег пользователя
    user_tag = get_user_tag(target_user_id)
    
    if not activities:
        activities_text = f"""
📊 <b>АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{target_user['username']}
<b>Тег:</b> {user_tag}
<b>ID:</b> <code>{target_user_id}</code>
<b>Роль:</b> {role}
<b>Регистрация:</b> {target_user.get('join_date', 'Неизвестно')}

<b>У этого пользователя пока нет зафиксированных действий.</b>
        """
    else:
        activities_per_page = 5
        total_pages = (len(activities) + activities_per_page - 1) // activities_per_page
        start_idx = page * activities_per_page
        end_idx = start_idx + activities_per_page
        
        activities_text = f"""
📊 <b>АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЯ</b>

<b>Пользователь:</b> @{target_user['username']}
<b>Тег:</b> {user_tag}
<b>ID:</b> <code>{target_user_id}</code>
<b>Роль:</b> {role}
<b>Всего действий:</b> {len(activities)}
<b>Страница:</b> {page + 1}/{total_pages}

<b>Последние действий:</b>
"""
        
        for i, activity in enumerate(activities[start_idx:end_idx], start_idx + 1):
            deal_ref = f"\n   Сделка: #{activity['deal_id'][:8]}" if activity.get('deal_id') else ""
            details = f"\n   Подробности: {activity['details']}" if activity.get('details') else ""
            
            activities_text += f"""
{i}. <b>{activity['action']}</b>
   ⏰ Время: {activity['timestamp']}{deal_ref}{details}
   ───────────────────
"""
    
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # Навигация по страницам
    if len(activities) > 5:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'admin_user_activity_{target_user_id}_{page-1}'))
        
        nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
        
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'admin_user_activity_{target_user_id}_{page+1}'))
        
        if nav_buttons:
            keyboard.add(*nav_buttons)
    
    keyboard.add(
        InlineKeyboardButton("👤 Профиль", callback_data=f'admin_view_user_{target_user_id}'),
        InlineKeyboardButton("✉️ Написать", callback_data=f'admin_message_user_{target_user_id}')
    )
    
    # Кнопка блокировки/разблокировки (только для владельцев)
    if user_id in owners:
        if is_user_blocked(target_user_id):
            keyboard.add(InlineKeyboardButton("✅ Разблокировать", callback_data=f'unblock_user_{target_user_id}'))
        else:
            keyboard.add(InlineKeyboardButton("🚫 Заблокировать", callback_data=f'block_user_{target_user_id}'))
    
    keyboard.add(InlineKeyboardButton("🔙 К списку", callback_data='user_activities_admin'))
    
    send_photo_message(chat_id, message_id, activities_text, keyboard)