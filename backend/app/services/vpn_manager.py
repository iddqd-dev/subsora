import json
import uuid
import logging
import os
import asyncio
import docker
from docker import errors
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.plan import Plan
from backend.app.models.subscription import Subscription
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

try:
    import grpc
    from backend.app.services.generated.app.proxyman.command import (  # type: ignore
        command_pb2,
        command_pb2_grpc,
    )
    from backend.app.services.generated.proxy.vless import account_pb2  # type: ignore
    from backend.app.services.generated.common.protocol import user_pb2  # type: ignore
    from backend.app.services.generated.common.serial import (  # type: ignore
        typed_message_pb2,
    )
except ImportError:
    # В проде эти модули должны быть доступны (генерятся из proto Xray).
    # Локально / в окружении без gRPC просто поднимем осмысленную ошибку при попытке использования.
    grpc = None
    command_pb2 = command_pb2_grpc = account_pb2 = user_pb2 = typed_message_pb2 = None


class VpnManager:
    def __init__(self):
        # Путь, куда Backend будет писать конфиг (внутри своего контейнера)
        # Это путь к примонтированному volume
        self.config_path = os.getenv("XRAY_CONFIG_PATH", "/etc/xray_shared/config.json")

        # Имя контейнера Xray, который мы будем пинать
        self.container_name = os.getenv("XRAY_CONTAINER_NAME", "subsora-xray")

        # Подключаемся к Docker Socket
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to connect to Docker Socket: {e}")
            self.docker_client = None

        # Настройки доступа к gRPC API Xray
        # По умолчанию предполагаем, что контейнер Xray доступен по имени "xray" в docker‑сети.
        self.api_addr = os.getenv(
            "XRAY_API_ADDR",
            getattr(settings, "XRAY_API_ADDR", "xray:10085"),
        )
        # Тег inbound'а, в который добавляем пользователей (должен совпадать с конфигом Xray).
        # В xray-admin использовался тег "vless-in".
        self.inbound_tag = os.getenv(
            "XRAY_INBOUND_TAG",
            getattr(settings, "XRAY_INBOUND_TAG", "vless-in"),
        )
        self.default_flow = "xtls-rprx-vision"

        # Ключи и параметры для генерации VLESS‑линка
        self.private_key = settings.XRAY_PRIVATE_KEY
        self.public_key = settings.XRAY_PUBLIC_KEY
        self.short_ids = [settings.XRAY_SHORT_ID] if hasattr(settings, "XRAY_SHORT_ID") else [""]
        self.server_names = ["yahoo.com", "www.yahoo.com"]
        self.dest = "yahoo.com:443"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.docker_client:
            self.docker_client.close()

    # == gRPC helpers ==

    def _ensure_grpc_available(self) -> None:
        if grpc is None:
            raise RuntimeError("Xray gRPC stubs are not available in this environment")

    def _pack_account(self, uid: str, flow: str | None = None):
        """Собираем TypedMessage с VLESS‑аккаунтом."""
        self._ensure_grpc_available()
        account = account_pb2.Account(id=uid, flow=flow or self.default_flow)
        return typed_message_pb2.TypedMessage(
            type="xray.proxy.vless.Account",
            value=account.SerializeToString(),
        )

    def _add_user_sync(self, email: str, uid: str, flow: str | None = None) -> None:
        """Синхронное добавление пользователя в inbound через gRPC."""
        self._ensure_grpc_available()
        channel = grpc.insecure_channel(self.api_addr)
        try:
            stub = command_pb2_grpc.HandlerServiceStub(channel)
            op = command_pb2.AddUserOperation(
                user=user_pb2.User(
                    email=email,
                    account=self._pack_account(uid, flow),
                )
            )
            req = command_pb2.AlterInboundRequest(
                tag=self.inbound_tag,
                operation=typed_message_pb2.TypedMessage(
                    type="xray.app.proxyman.command.AddUserOperation",
                    value=op.SerializeToString(),
                ),
            )
            stub.AlterInbound(req)
        finally:
            channel.close()

    async def _add_user(self, email: str, uid: str, flow: str | None = None) -> None:
        """Асинхронная обёртка над _add_user_sync, чтобы не блокировать event‑loop."""
        await asyncio.to_thread(self._add_user_sync, email, uid, flow)

    def _remove_user_sync(self, email: str) -> None:
        """Синхронное удаление пользователя из inbound через gRPC."""
        self._ensure_grpc_available()
        channel = grpc.insecure_channel(self.api_addr)
        try:
            stub = command_pb2_grpc.HandlerServiceStub(channel)
            op = command_pb2.RemoveUserOperation(email=email)
            req = command_pb2.AlterInboundRequest(
                tag=self.inbound_tag,
                operation=typed_message_pb2.TypedMessage(
                    type="xray.app.proxyman.command.RemoveUserOperation",
                    value=op.SerializeToString(),
                ),
            )
            stub.AlterInbound(req)
        finally:
            channel.close()

    async def _remove_user(self, email: str) -> None:
        """Асинхронная обёртка над _remove_user_sync."""
        await asyncio.to_thread(self._remove_user_sync, email)

    def _get_xray_container(self):
        """Находит контейнер Xray"""
        if not self.docker_client:
            raise RuntimeError("Docker client not initialized")
        try:
            # Ищем по имени или ID
            return self.docker_client.containers.get(self.container_name)
        except docker.errors.NotFound:
            logger.error(f"Container {self.container_name} not found")
            return None

    def _get_base_config(self) -> Dict[str, Any]:
        """Базовый конфиг"""
        return {
            "log": {
                "loglevel": "warning",
                # Пути внутри контейнера Xray!
                "access": "/app/log/xray/access.log",
                "error": "/app/log/xray/error.log"
            },
            "api": {
                "tag": "api",
                "services": ["HandlerService", "LoggerService", "StatsService"]
            },
            "stats": {},
            "policy": {
                "levels": {
                    "0": {
                        "statsUserUplink": True,
                        "statsUserDownlink": True
                    }
                },
                "system": {
                    "statsInboundUplink": True,
                    "statsInboundDownlink": True
                }
            },
            "inbounds": [
                {
                    "tag": "vless-reality",
                    "port": 443,
                    "protocol": "vless",
                    "settings": {
                        "clients": [],
                        "decryption": "none"
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "reality",
                        "realitySettings": {
                            "show": False,
                            "dest": self.dest,
                            "serverNames": self.server_names,
                            "privateKey": self.private_key,
                            "shortIds": self.short_ids
                        }
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    }
                }
            ],
            "outbounds": [
                {"protocol": "freedom", "tag": "direct"},
                {"protocol": "blackhole", "tag": "block"}
            ]
        }

    async def _regenerate_and_reload(self, db):
        """Генерация конфига и Hot Reload"""
        logger.info("🔄 Regenerating Xray config...")

        now = datetime.now(timezone.utc)
        query = (select(Subscription).join(User).where(Subscription.end_date > now))
        result = await db.execute(query)
        active_subs = result.scalars().all()

        config = self._get_base_config()
        clients = []

        for sub in active_subs:
            user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(sub.user_id)))
            clients.append({
                "id": user_uuid,
                "flow": "xtls-rprx-vision",
                "email": f"user_{sub.user_id}"
            })

        config["inbounds"][0]["settings"]["clients"] = clients

        # 1. Пишем файл в общий volume
        try:
            # os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Config written to {self.config_path}")
        except IOError as e:
            logger.error(f"❌ Failed to write config: {e}")
            raise

        # 2. Отправляем SIGHUP контейнеру
        container = self._get_xray_container()
        if container:
            try:
                container.kill(signal="SIGHUP")
                logger.info(f"✅ Sent SIGHUP to container {self.container_name}")
            except Exception as e:
                logger.error(f"❌ Failed to reload container: {e}")
        else:
            logger.warning("⚠️ Xray container not found, skipping reload")

    def generate_link(self, user_id: int, user_email: str) -> str:
        user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user_id)))
        sni = self.server_names[0]
        sid = self.short_ids[0]
        host = settings.VPN_PANEL_URL.replace("https://", "").replace("http://", "")

        link = (
            f"vless://{user_uuid}@{host}:443"
            f"?security=reality&encryption=none&pbk={self.public_key}"
            f"&headerType=none&fp=chrome&type=tcp&flow=xtls-rprx-vision"
            f"&sni={sni}&sid={sid}#Subsora-{user_email}"
        )
        return link

    async def provision_user(self, user: User, plan: Plan) -> Dict[str, str]:
        """
        Создает/обновляет пользователя в Xray через gRPC и возвращает ссылку VLESS.
        """
        user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user.id)))

        try:
            await self._add_user(email=user.email, uid=user_uuid, flow=self.default_flow)
            logger.info("✅ Xray gRPC: user %s added/updated (uuid=%s)", user.email, user_uuid)
        except Exception as e:
            logger.error("❌ Failed to provision user in Xray via gRPC: %s", e)
            raise

        link = self.generate_link(user.id, user.email)
        return {"subscription_url": link}

    async def sync_active_users(self, db: AsyncSession) -> None:
        """
        Синхронизирует состояние Xray с нашей БД:
        для всех активных подписок гарантирует наличие пользователя в Xray.
        """
        now = datetime.now(timezone.utc)
        query = (
            select(Subscription, User)
            .join(User, Subscription.user_id == User.id)
            .where(Subscription.end_date > now)
        )
        result = await db.execute(query)
        rows = result.fetchall()

        total = 0
        for sub, user in rows:
            total += 1
            user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user.id)))
            try:
                await self._add_user(email=user.email, uid=user_uuid, flow=self.default_flow)
            except Exception as e:
                logger.error(
                    "❌ Failed to sync user %s (uuid=%s) to Xray: %s",
                    user.email,
                    user_uuid,
                    e,
                )
        logger.info("✅ Xray sync finished, processed %s active users", total)

    async def drop_user_from_xray_runtime(self, user: User) -> None:
        """
        Технически удаляет пользователя из рантайма Xray (gRPC RemoveUserOperation),
        не затрагивая сущность пользователя и историю подписок в Postgres.

        Полное удаление (remove) в нашем домене должно делать отдельная бизнес‑логика,
        которая сначала корректно меняет/чистит данные в БД, а уже затем при необходимости
        вызывает этот метод как часть финального "purge".
        """
        try:
            await self._remove_user(email=user.email)
            logger.info("✅ Xray gRPC: user %s removed from Xray runtime", user.email)
        except Exception as e:
            logger.error(
                "❌ Failed to remove user %s from Xray runtime via gRPC: %s",
                user.email,
                e,
            )

    async def get_user_stats(self, username: str) -> Dict:
        return {"used_traffic": 0, "data_limit": 0, "status": "active", "online_at": None, "expire": None}

    # 👇 УПРАВЛЕНИЕ КОНТЕЙНЕРОМ 👇

    async def restart_core(self):
        """Рестарт контейнера"""
        container = self._get_xray_container()
        if container:
            container.restart()
            return "success"
        return "failed"

    async def start_core(self):
        """Старт контейнера"""
        container = self._get_xray_container()
        if container:
            container.start()
            return "success"
        return "failed"

    async def stop_core(self):
        """Стоп контейнера"""
        container = self._get_xray_container()
        if container:
            container.stop()
            return "success"
        return "failed"

    async def get_system_stats(self):
        """Статистика контейнера (не хоста!)"""
        # Если нужно именно потребление Xray
        container = self._get_xray_container()
        if container:
            stats = container.stats(stream=False)
            # Тут можно распарсить JSON от докера, чтобы получить CPU/RAM конкретного контейнера
            # Но для простоты вернем общую заглушку или можно использовать psutil внутри backend контейнера (покажет usage backend'а)
            return {
                "version": "Containerized Xray",
                "status": container.status,
                "users_active": 0,
                "total_user": 0
            }
        return {"error": "Container not found"}