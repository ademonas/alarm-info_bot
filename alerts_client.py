import aiohttp
import logging

logger = logging.getLogger(__name__)

class AlertsClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.alerts.in.ua/v1/alerts/active.json"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    async def get_status(self) -> dict:
        """
        Возвращает словарь: {"status": "active"|"clear", "threat_type": "Причина"|None}
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, headers=self.headers, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    result = {"status": "clear", "threat_type": None}
                    
                    if "alerts" in data:
                        for alert in data["alerts"]:
                            location = alert.get("location_title", "")
                            if "Харківська область" in location or "м. Харків" in location:
                                result["status"] = "active"
                                # Если API отдает тип угрозы (название поля зависит от реального API)
                                result["threat_type"] = alert.get("notes", "Невідома загроза")
                                break
                                
                    return result
            except Exception as e:
                logger.error(f"Ошибка запроса к API: {e}")
                raise
