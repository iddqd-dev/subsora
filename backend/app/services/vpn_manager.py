import json
import uuid
import logging
import os
import docker
from docker import errors
from typing import Dict, Any
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.plan import Plan
from backend.app.models.subscription import Subscription
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


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

        self.private_key = settings.XRAY_PRIVATE_KEY
        self.public_key = settings.XRAY_PUBLIC_KEY
        self.short_ids = [settings.XRAY_SHORT_ID] if hasattr(settings, 'XRAY_SHORT_ID') else [""]
        self.server_names = ["yahoo.com", "www.yahoo.com"]
        self.dest = "yahoo.com:443"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.docker_client:
            self.docker_client.close()

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

        now = datetime.now(UTC)
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
        from backend.app.db.session import get_async_session
        async with get_async_session() as db:
            await self._regenerate_and_reload(db)
        link = self.generate_link(user.id, user.email)
        return {"subscription_url": link}

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