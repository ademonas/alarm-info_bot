import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHANNEL_ID = os.getenv("CHANNEL_ID")
    ALERTS_API_TOKEN = os.getenv("ALERTS_API_TOKEN")

    @classmethod
    def validate(cls):
        missing = [k for k, v in [("BOT_TOKEN", cls.BOT_TOKEN), ("CHANNEL_ID", cls.CHANNEL_ID), ("ALERTS_API_TOKEN", cls.ALERTS_API_TOKEN)] if not v]
        if missing:
            raise ValueError(f"Отсутствуют переменные: {', '.join(missing)}")

config = Config()
try:
    config.validate()
except ValueError as e:
    logging.error(f"Ошибка конфигурации: {e}")
    sys.exit(1)
