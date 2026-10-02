from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.db_manager import DBManager
import os
import uuid

from admin.filters import IsAdmin
from admin.keyboards import get_admin_main_keyboard, get_confirm_keyboard
from core.telegram_publisher import TelegramPublisher

# Создаем роутер для админки и сразу применяем фильтр ко всем сообщениям
admin_router = Router()
admin_router.message.filter(IsAdmin())
db = DBManager()

# Определяем состояния для FSM
class PublishNews(StatesGroup):
    waiting_for_text = State()
    confirm_publish = State()

class AddAdminFSM(StatesGroup):
    waiting_for_username = State()

@admin_router.message(Command("admin"))
async def cmd_admin_start(message: Message, state: FSMContext):
    """Вход в админ-панель."""
    await state.clear() # Сбрасываем возможные зависшие состояния
    await message.answer(
        "Добро пожаловать в панель управления AlarmInfo-Bot.",
        reply_markup=get_admin_main_keyboard()
    )

@admin_router.message(F.text == "👥 Добавить админа")
async def cmd_add_admin(message: Message, state: FSMContext):
    await message.answer(
        "Введите `username` нового администратора (с символом @ или без него):", 
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(AddAdminFSM.waiting_for_username)

@admin_router.message(AddAdminFSM.waiting_for_username)
async def process_new_admin(message: Message, state: FSMContext, db_manager: DBManager):
    new_username = message.text
    # Записываем в БД (очистка от @ происходит внутри метода add_admin)
    await db_manager.add_admin(new_username)
    
    clean_username = new_username.replace("@", "").strip()
    await message.answer(
        f"✅ Пользователь @{clean_username} успешно добавлен в список администраторов!\n"
        "Теперь он может управлять ботом.",
        reply_markup=get_admin_main_keyboard()
    )
    await state.clear()

@admin_router.message(F.text == "📊 Статус сервиса")
async def cmd_status(message: Message):
    """Генерация сводки по тревогам для администратора."""
    # Получаем статистику из базы данных
    stats = await db.get_daily_stats()
    count = stats.get("daily_count", 0)
    
    # Генерируем уникальный номер билда (первые 7 символов случайного хэша)
    dynamic_build = uuid.uuid4().hex[:7]
    
    text = (
        "📊 **Статус сервісу (Харків):**\n\n"
        f"🔴 Кількість тривог за сьогодні: **{count}**\n"
        "🟢 Система працює в штатному режимі.\n\n"
        f"**Версія бота:** 1.3.0\n"
        f"**Поточний білд:** `{dynamic_build}`"
    )
    await message.answer(text, parse_mode="Markdown")

@admin_router.message(F.text == "📊 Статус сервиса")
async def cmd_status(message: Message):
    """Генерация сводки по тревогам для администратора[cite: 8]."""
    stats = await db.get_daily_stats()
    count = stats.get("daily_count", 0)
    
    text = (
        "📊 **Статус сервісу (ИнфаОтРубика):**\n\n"
        f"🔴 Кількість тривог за сьогодні: **{count}**\n"
        "🟢 Система працює в штатному режимі."
    )
    await message.answer(text, parse_mode="Markdown")

# --- Логика FSM для ручной публикации ---

@admin_router.message(F.text == "📢 Отправить новость вручную")
async def start_manual_publish(message: Message, state: FSMContext):
    """Шаг 1: Запрашиваем текст новости."""
    await message.answer("Введите текст новости, который нужно отправить в канал:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PublishNews.waiting_for_text)

@admin_router.message(PublishNews.waiting_for_text)
async def process_news_text(message: Message, state: FSMContext):
    """Шаг 2: Получили текст, просим подтверждения."""
    await state.update_data(news_text=message.text)
    await message.answer(
        f"Вы собираетесь отправить следующее сообщение:\n\n{message.text}\n\nПодтверждаете отправку?",
        reply_markup=get_confirm_keyboard()
    )
    await state.set_state(PublishNews.confirm_publish)

@admin_router.message(PublishNews.confirm_publish, F.text.in_(["✅ Так", "❌ Ні"]))
async def confirm_news_publish(message: Message, state: FSMContext, bot: Bot):
    """Шаг 3: Обрабатываем подтверждение и отправляем в канал."""
    if message.text == "❌ Ні":
        await message.answer("Отправка отменена.", reply_markup=get_admin_main_keyboard())
        await state.clear()
        return

    # Получаем сохраненный текст из FSM
    user_data = await state.get_data()
    text_to_publish = user_data.get("news_text")
    channel_id = os.getenv("CHANNEL_ID")

    try:
        # Отправляем сообщение напрямую в канал
        await bot.send_message(chat_id=channel_id, text=text_to_publish)
        await message.answer("✅ Новость успешно опубликована в канале!", reply_markup=get_admin_main_keyboard())
    except Exception as e:
         await message.answer(f"❌ Ошибка при отправке: {e}", reply_markup=get_admin_main_keyboard())
    
    await state.clear()
