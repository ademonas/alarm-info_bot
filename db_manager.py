import aiosqlite
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class DBManager:
    """Управление базой данных SQLite для хранения истории тревог и генерации сводок."""
    def __init__(self, db_path: str = "alerts.db"):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация схемы БД с правильными индексами для быстрых выборок."""
        async with aiosqlite.connect(self.db_path) as db:
            # 1. Таблица истории тревог
            await db.execute('''
                CREATE TABLE IF NOT EXISTS alerts_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status VARCHAR(50) NOT NULL,
                    threat_type VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Индекс для ускорения аналитических запросов по дате
            await db.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts_history(timestamp)')
            
            # 2. НОВАЯ ТАБЛИЦА: Администраторы
            await db.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(255) UNIQUE NOT NULL
                )
            ''')
            
            await db.commit()
            logger.info("Схема базы данных успешно проинициализирована.")

    async def log_event(self, status: str, threat_type: str = None):
        """Запись события изменения статуса в историю."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO alerts_history (status, threat_type) VALUES (?, ?)",
                (status, threat_type)
            )
            await db.commit()

    async def get_daily_stats(self) -> dict:
        """Сбор статистики за текущий день."""
        async with aiosqlite.connect(self.db_path) as db:
            # Считаем количество тревог за сегодня
            cursor = await db.execute('''
                SELECT COUNT(*) FROM alerts_history 
                WHERE status = 'active' AND date(timestamp) = date('now', 'localtime')
            ''')
            count = (await cursor.fetchone())[0]
            
            return {"daily_count": count}

    # --- НОВЫЕ МЕТОДЫ ДЛЯ АДМИНОВ ---
    
    async def add_admin(self, username: str):
        """Добавляет нового администратора по username."""
        # Очищаем от @ если пользователь ввел его случайно
        clean_username = username.replace("@", "").strip()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO admins (username) VALUES (?)", (clean_username,))
            await db.commit()

    async def is_admin(self, username: str) -> bool:
        """Проверяет, есть ли username в базе администраторов."""
        if not username:
            return False
            
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT 1 FROM admins WHERE username = ?", (username,))
            result = await cursor.fetchone()
            return bool(result)
