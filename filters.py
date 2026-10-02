import os
from aiogram.filters import BaseFilter
from aiogram.types import Message
from core.db_manager import DBManager

class IsAdmin(BaseFilter):
    """Фильтр для проверки, является ли пользователь администратором."""
    # Добавляем db_manager в аргументы (aiogram передаст его автоматически из dp)
    async def __call__(self, message: Message, db_manager: DBManager) -> bool:
        # 1. Проверка на "Суперадмина" из .env
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip().isdigit()]
        
        if message.from_user.id in admin_ids:
            return True
            
        # 2. Проверка по username в базе данных
        if message.from_user.username:
            is_db_admin = await db_manager.is_admin(message.from_user.username)
            return is_db_admin
            
        return False
