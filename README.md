Subsora
Система управления подписками и автоматизации VPN-инфраструктуры (Xray/Hysteria).
Технологический стек:
— Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic.
— Infrastructure: PostgreSQL, Redis, Docker Compose.
— CI/CD: Drone CI (автоматизация сборки и деплоя).
— Integration: Telegram Bot API (aiogram), Xray API (gRPC).
Ключевой функционал:
— Автоматическая синхронизация активных пользователей с Xray-ядром.
— Управление жизненным циклом подписок через Telegram-бота.
— Логирование инцидентов и системных событий.
— Полностью контейнеризированное окружение.
Развертывание:
Настроить окружение в .env.
Запуск: docker compose up -d --build.
Миграции: Применяются автоматически при старте контейнера через init-скрипт.
