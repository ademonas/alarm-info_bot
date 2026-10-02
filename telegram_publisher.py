import logging
import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

logger = logging.getLogger(__name__)

class TelegramPublisher:
    def __init__(self, bot: Bot, channel_id: str):
        self.bot = bot
        self.channel_id = channel_id

    async def publish(self, status: str, threat_type: str = None) -> bool:
        if status == "active":
            text = "🚨 **УВАГА! Повітряна тривога: Харків та область!** 🚨"
            # Добавляем информацию об угрозе, если она известна
            if threat_type and threat_type != "Невідома загроза":
                text += f"\n⚠️ **Загроза:** {threat_type}"
        elif status == "clear":
            text = "🟢 **Відбій повітряної тривоги!** 🟢"
        else:
            text = f"ℹ️ Статус змінено: {status}"

        try:
            await self.bot.send_message(chat_id=self.channel_id, text=text, parse_mode="Markdown")
            logger.info("Сообщение успешно отправлено в канал.")
            return True
        except TelegramRetryAfter as e:
            logger.error(f"Лимит запросов. Ожидание {e.retry_after} сек.")
            await asyncio.sleep(e.retry_after)
            return await self.publish(status, threat_type)
        except TelegramAPIError as e:
            logger.error(f"Ошибка Telegram API: {e}")
            return False
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при отправке: {e}")
            return False
