# AlarmInfo-Bot

Telegram-бот, который следит за статусом воздушной тревоги в Харькове и Харьковской области через [alerts.in.ua](https://alerts.in.ua) и публикует изменения в Telegram-канал. Включает админ-панель прямо в Telegram.

## Возможности

- Опрос API alerts.in.ua каждые 15 секунд
- Публикация в канал при начале тревоги (с типом угрозы, если он известен) и при отбое
- История событий в SQLite (`alerts.db`) и дневная статистика
- Админ-панель (`/admin`):
  - ручная публикация новости в канал с подтверждением
  - статус сервиса и число тревог за сегодня
  - добавление администраторов по username

## Требования

- Python 3.10+ (проект разрабатывался на 3.12)
- Telegram-бот (токен от [@BotFather](https://t.me/BotFather))
- Telegram-канал, где бот назначен администратором с правом публикации
- Токен API [alerts.in.ua](https://alerts.in.ua/api-request)

## Установка

```bash
git clone https://github.com/<your-username>/alarm-info-bot.git
cd alarm-info-bot

python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Настройка

Скопируйте шаблон и заполните значения:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

| Переменная | Обязательна | Описание |
|---|---|---|
| `BOT_TOKEN` | да | Токен бота от @BotFather |
| `CHANNEL_ID` | да | ID канала (`-100...`) или `@username` публичного канала |
| `ALERTS_API_TOKEN` | да | Токен API alerts.in.ua |
| `ADMIN_IDS` | нет | Telegram ID суперадминов через запятую |

**Как получить ID канала:** добавьте бота в канал администратором, отправьте любое сообщение и откройте `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`, либо воспользуйтесь ботом вроде @getmyid_bot. Свой Telegram ID для `ADMIN_IDS` можно узнать там же.

## Запуск

```bash
python main.py
```

При первом запуске автоматически создаётся `alerts.db`. Первое полученное состояние API в канал не публикуется, чтобы не спамить при перезапуске.

Для постоянной работы на сервере можно использовать `systemd`, `screen`/`tmux` или Docker.

<details>
<summary>Пример systemd-юнита</summary>

```ini
[Unit]
Description=AlarmInfo Bot
After=network-online.target

[Service]
WorkingDirectory=/opt/alarm-info-bot
ExecStart=/opt/alarm-info-bot/venv/bin/python main.py
Restart=always
User=bot

[Install]
WantedBy=multi-user.target
```
</details>

## Админ-панель

1. Укажите свой Telegram ID в `ADMIN_IDS` (суперадмин), перезапустите бота.
2. Отправьте боту `/admin`.
3. Дополнительных админов добавляйте кнопкой «👥 Добавить админа» (по username).

## Структура проекта

```
.
├── main.py                   # точка входа, цикл опроса API
├── requirements.txt
├── .env.example
├── admin/
│   ├── filters.py            # фильтр IsAdmin
│   ├── handlers.py           # команды и FSM админ-панели
│   └── keyboards.py          # клавиатуры
├── api_client/
│   └── alerts_client.py      # клиент alerts.in.ua
└── core/
    ├── config.py             # загрузка и проверка .env
    ├── db_manager.py         # SQLite: история тревог, админы
    ├── state_manager.py      # отслеживание смены статуса
    └── telegram_publisher.py # отправка сообщений в канал
```

## Безопасность

- Никогда не коммитьте `.env` и `alerts.db` (они уже в `.gitignore`).
- Если токен попал в публичный доступ, немедленно перевыпустите его через @BotFather (`/revoke`).

## Стек

Python, [aiogram 3](https://docs.aiogram.dev), aiohttp, aiosqlite, python-dotenv.
