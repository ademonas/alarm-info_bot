import logging
from typing import Tuple, Optional
from core.db_manager import DBManager

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self._current_state: Optional[str] = None

    async def check_and_update(self, new_data: dict) -> Tuple[bool, dict]:
        """
        Сравнивает новый статус с текущим in-memory. Если статус изменился,
        логирует его в БД и возвращает True.
        """
        new_status = new_data["status"]
        threat_type = new_data.get("threat_type")

        if self._current_state != new_status:
            logger.info(f"Смена состояния: {self._current_state} -> {new_status}")
            
            is_initial_run = self._current_state is None
            self._current_state = new_status
            
            # Записываем событие в базу данных (вместо JSON-файла)
            await self.db.log_event(status=new_status, threat_type=threat_type)
            
            # Если это первый запуск, не отправляем уведомление, чтобы не спамить
            return not is_initial_run, new_data
        
        return False, new_data
