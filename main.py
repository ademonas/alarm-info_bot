import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from core.config import config
from api_client.alerts_client import AlertsClient
from core.state_manager import StateManager
from core.telegram_publisher import TelegramPublisher
from core.db_manager import DBManager

# Импортируем роутер админки
from admin.handlers import admin_router 

async def poll_api(client: AlertsClient, state: StateManager, publisher: TelegramPublisher):
    logger = logging.getLogger("api_poller")
    while True:
        try:
            status_data = await client.get_status() # Возвращает dict
            has_changed, current_data = await state.check_and_update(status_data)
            
            if has_changed:
                status = current_data["status"]
                threat_type = current_data.get("threat_type")
                
                logger.info(f"Статус изменился: {status} | Угроза: {threat_type}")
                # Передаем статус и тип угрозы в паблишер
                await publisher.publish(status, threat_type=threat_type)
        except Exception as e:
            logger.error(f"Ошибка при опросе API: {e}")
        
        await asyncio.sleep(15)

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
    logger = logging.getLogger(__name__)
    logger.info("Запуск AlarmInfo-Bot (Phase 1, 2 & 3)...")

    bot = Bot(token=config.BOT_TOKEN)
    
    # Добавляем MemoryStorage для работы FSM
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем роутер админки к диспетчеру
    dp.include_router(admin_router)
    
    # --- ИЗМЕНЕНИЯ ЗДЕСЬ ---
    # 1. Инициализируем базу данных и создаем таблицы
    db_manager = DBManager()
    await db_manager.init_db()

    dp["db_manager"] = db_manager
    
    alerts_client = AlertsClient(api_token=config.ALERTS_API_TOKEN)
    
    # 2. Передаем db_manager внутрь StateManager
    state_manager = StateManager(db_manager=db_manager)
    # -----------------------
    
    publisher = TelegramPublisher(bot=bot, channel_id=config.CHANNEL_ID)

    api_polling_task = asyncio.create_task(poll_api(alerts_client, state_manager, publisher))

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Остановка бота...")
        api_polling_task.cancel()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен вручную.")
