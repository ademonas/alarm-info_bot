from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает главную клавиатуру для админ-панели."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Отправить новость вручную")],
            [KeyboardButton(text="📊 Статус сервиса"), KeyboardButton(text="⚙️ Настройки")]
        ],
        resize_keyboard=True,
        persistent=True # Клавиатура будет оставаться открытой
    )
    return keyboard

def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для подтверждения отправки (Так/Ні)."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Так"), KeyboardButton(text="❌ Ні")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True # Скрывается после нажатия
    )
    return keyboard

def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Отправить новость вручную")],
            [KeyboardButton(text="📊 Статус сервиса"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="👥 Добавить админа")] # НОВАЯ КНОПКА
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard
