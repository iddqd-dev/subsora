import logging
import uuid
from datetime import datetime, timedelta

# --- Новые, правильные импорты из архитектуры Subsora ---
from backend.app.core.config import settings
from backend.app.marzpy import Marzban
from backend.app.marzpy.api.user import User as MarzbanUser
from backend.app.models.user import User as SubsoraUser  # Наша SQLAlchemy модель пользователя
from backend.app.models.plan import Plan as SubsoraPlan  # Наша SQLAlchemy модель плана


# ❌ Старые импорты удалены. Нам не нужна локализация, репозитории или utils из старого проекта.
# Вспомогательные функции, если понадобятся, мы перенесем или перепишем.

# Вспомогательные функции (можно вынести в app/utils/helpers.py)
def bytes_to_gb(bytes_value: int) -> float:
    if not isinstance(bytes_value, (int, float)) or bytes_value < 0:
        return 0.0
    return round(bytes_value / (1024 ** 3), 2)


class VpnManager:
    def __init__(self):
        self.host_url = f"{settings.VPN_PANEL_URL}:{settings.VPN_PANEL_PORT}"
        self.username = settings.VPN_PANEL_USER
        self.password = settings.VPN_PANEL_PASSWORD
        self.panel: Marzban | None = None
        self.token: dict | None = None
        self.authenticated = False

    async def __aenter__(self):
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Marzpy сам управляет сессией, здесь ничего не нужно
        pass

    async def authenticate(self):
        if self.authenticated:
            return True
        try:
            self.panel = Marzban(
                username=self.username,
                password=self.password,
                panel_address=self.host_url
            )
            self.token = await self.panel.get_token()
            if not self.token:
                logging.error("Failed to authenticate with Marzban: No token received")
                self.authenticated = False
                return False

            logging.info("Successfully authenticated with Marzban")
            self.authenticated = True
            return True
        except Exception as e:
            logging.error(f"Marzban authentication error: {e}")
            self.authenticated = False
            return False

    async def generate_subscription_link(self, username: str) -> str | None:
        if not self.authenticated or not self.panel:
            raise ConnectionError("Marzban client is not authenticated.")

        try:
            user = await self.panel.get_user(user_username=username, token=self.token)
            return f"{self.host_url}{user.subscription_url}"
        except Exception as e:
            logging.error(f"Failed to generate subscription link for {username}: {e}")
            return None

    # 👇 НОВЫЙ МЕТОД, который станет сердцем интеграции
    async def provision_user(self, user: SubsoraUser, plan: SubsoraPlan) -> dict:
        """
        Создает или обновляет пользователя в Marzban на основе данных из Subsora.
        """
        if not self.authenticated or not self.panel:
            raise ConnectionError("Marzban client is not authenticated.")

        # Определяем username для Marzban. Лучше использовать что-то уникальное, например, email.
        marzban_username = user.email

        # Вычисляем параметры на основе плана Subsora
        expiry_time = int((datetime.now() + timedelta(days=plan.duration_days)).timestamp())
        data_limit_gb = 30  # Здесь можно добавить поле data_limit_gb в модель Plan
        data_limit_bytes = data_limit_gb * (1024 ** 3) if data_limit_gb > 0 else 0

        try:
            # Пытаемся получить существующего пользователя
            existing_marzban_user = await self.panel.get_user(user_username=marzban_username, token=self.token)
        except Exception:
            existing_marzban_user = None

        if existing_marzban_user:
            # --- Логика обновления пользователя ---
            logging.info(f"Updating existing Marzban user: {marzban_username}")
            existing_marzban_user.expire = expiry_time
            existing_marzban_user.data_limit = data_limit_bytes
            existing_marzban_user.status = "active"
            await self.panel.modify_user(user_username=marzban_username, token=self.token, user=existing_marzban_user)
        else:
            # --- Логика создания нового пользователя ---
            logging.info(f"Creating new Marzban user: {marzban_username}")
            new_marzban_user = MarzbanUser(
                username=marzban_username,
                proxies={"vless": {"id": str(uuid.uuid4())}},
                inbounds={"vless": ["inbound-7443"]},  # Укажи правильный inbound
                expire=expiry_time,
                data_limit=data_limit_bytes,
                note=f"Subsora user_id: {user.id}"
            )
            await self.panel.add_user(user=new_marzban_user, token=self.token)

        # Получаем и возвращаем ссылку
        subscription_url = await self.generate_subscription_link(marzban_username)
        if not subscription_url:
            raise RuntimeError(f"Could not get subscription URL for user {marzban_username}")

        return {"subscription_url": subscription_url}

    async def get_user_stats(self, username: str) -> dict:
        """
        Получает расширенную статистику для пользователя из Marzban.
        """
        if not self.authenticated or not self.panel or not self.token:
            raise ConnectionError("Marzban client is not authenticated.")

        try:
            user_data = await self.panel.get_user(user_username=username, token=self.token)

            # 👇 ВОТ ИСПРАВЛЕНИЕ: Возвращаем все поля, которые требует схема VpnStats

            # Парсим строковую дату, если она есть
            online_at_datetime = None
            if user_data.online_at:
                try:
                    # Marzban возвращает строку в формате ISO 8601 с 'Z'
                    online_at_datetime = datetime.fromisoformat(user_data.online_at.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    online_at_datetime = None  # Если формат кривой, просто игнорируем

            return {
                "used_traffic": user_data.used_traffic,
                "data_limit": user_data.data_limit,
                "status": user_data.status,
                "online_at": online_at_datetime,
                "expire": user_data.expire
            }

        except Exception as e:
            logging.error(f"Failed to get stats for user {username} from Marzban: {e}")
            raise

# import logging
# import uuid
# from datetime import datetime, timedelta
# from backend.app.marzpy import Marzban
# from backend.app.marzpy.api.user import User
# from backend.app.core.config import settings
# from core.database import get_db_session
# from core.utils.utils import generate_qr_code, format_time_difference, bytes_to_gb, bytes_to_mb
# from core.repositories.user_repo import UserRepository
# from core.localization import Localization
#
# ONE_DAY_MS = 86400000
# THREE_HOURS_MS = 10800000
#
# class MarzbanApi:
#     def __init__(self):
#         self.authenticated = None
#         self.host_url = f"{settings.VPN_PANEL_URL}:{settings.VPN_PANEL_PORT}"
#         self.username = settings.VPN_PANEL_USER
#         self.password = settings.VPN_PANEL_PASSWORD
#         self.ssl = getattr(settings, 'SSL', True)  # Default to HTTPS
#         self.panel = None
#         self.token = None
#
#     async def __aenter__(self):
#         await self.authenticate()
#         return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         # Marzpy handles session cleanup internally
#         pass
#
#     async def authenticate(self):
#         try:
#             self.panel = Marzban(
#                 username=self.username,
#                 password=self.password,
#                 panel_address=self.host_url
#             )
#             self.token = await self.panel.get_token()
#             logging.info(self.token)
#             if not self.token:
#                 logging.error("Failed to authenticate with Marzban")
#                 return False
#             self.authenticated = True
#             return True
#         except Exception as e:
#             logging.error(f"Authentication error: {e}")
#             return False
#
#     async def test_connect(self):
#         return await self.authenticate()
#
#     async def generate_subscription_link(self, username):
#         # Marzban subscription URLs are typically in the format: https://domain/sub/hash
#         subscription = (await self.panel.get_user(user_username=username, token=self.token)).subscription_url
#         return f"{self.host_url}{subscription}"
#
#     async def add_client(self, day, tg_id, user_id, fullname, test_mode=False, subscription_id=None, referral=None):
#         async with get_db_session() as db_session:
#             try:
#                 # Calculate expiration (Marzban uses Unix timestamp in seconds)
#                 expiry_time = int((datetime.now() + timedelta(days=day)).timestamp())
#                 # Define traffic limit (30GB for test mode, unlimited for premium)
#                 data_limit = 30 * 1024 * 1024 * 1024 if test_mode else 0  # 30GB in bytes
#                 username = user_id or str(tg_id)
#
#                 # Define user with VMess and VLESS protocols (similar to 3X-UI setup)
#                 user = User(
#                     username=username,
#                     proxies={
#                         "vless": {
#                             "id": str(uuid.uuid1()),
#                             "flow": "xtls-rprx-vision"
#                         },
#                     },
#                     inbounds={
#                         "vless": ["inbound-8443" if test_mode else "inbound-443"],
#                     },
#                     expire=expiry_time,
#                     data_limit=data_limit,
#                     data_limit_reset_strategy="no_reset",
#                     status="active",
#                     note= f"user id {tg_id}"
#                 )
#
#                 # Add user via Marzban API
#                 result = await self.panel.add_user(user=user, token=self.token)
#                 ur = UserRepository(db_session)
#                 if not result:
#                     logging.error(f"Failed to add user {username}")
#                     return Localization().gettext("error_default", error_id=str(uuid.uuid4())[:8]), None
#                 # Generate subscription URL
#                 subscription = await self.generate_subscription_link(username)
#                 qr_code_file = f"qr_codes/{username}_vpn_qr.png"
#                 generate_qr_code(subscription, qr_code_file)
#
#                 # Save user to database
#                 await ur.add_user(
#                     telegram_id=tg_id,
#                     username=username,
#                     fullname=fullname,
#                     subscription_url=subscription,
#                     expiry_time=str(expiry_time * 1000),  # Store as milliseconds for consistency
#                     used_test_period=1 if test_mode else 0,
#                     active_subscription_id=9 if test_mode else subscription_id
#                 )
#                 referrer = await ur.get_user_by_referral_link(referral)
#                 if referrer:
#                     logging.info('Referrer founded.')
#                     await ur.add_referral(referrer.user_id, tg_id)
#
#                 return self.prepare_client_text(fullname, subscription if not test_mode else '', expiry_time * 1000, data_limit), qr_code_file if not test_mode else ''
#             except Exception as e:
#                 error_id = str(uuid.uuid4())[:8]
#                 logging.error(f"Error adding user [{error_id}]: {e}")
#                 return Localization().gettext("error_default", error_id=error_id), None
#
#     @staticmethod
#     def prepare_client_text(fullname, subscription, expiry_time=None, bytes_left=None):
#         if expiry_time:
#             logging.info(f'User {fullname} already registered.')
#             return Localization().gettext("registration_already_exists",
#                                          fullname=fullname,
#                                          subscription=subscription,
#                                          expiry_time=format_time_difference(expiry_time),
#                                          bytes_left=bytes_to_gb(bytes_left))
#         logging.info(f'User {fullname} successfully registered.')
#         return Localization().gettext("registration_successful",
#                                      fullname=fullname,
#                                      subscription=subscription)
#
#     async def account(self, tg_id, user_id):
#         try:
#             # Fetch user data
#             user = await self.panel.get_user(user_username=user_id, token=self.token)
#             if not user:
#                 return Localization().gettext("account_not_registered")
#
#             # Fetch usage data
#             usage = await self.panel.get_user_usage(user_username=user_id, token=self.token)
#             total_used_traffic = usage['used_traffic']
#
#             # Calculate traffic left
#             traffic_left = user.data_limit - total_used_traffic if user.data_limit else 0
#
#             # Format response
#             result = Localization().gettext("account_subscription_details",
#                                            separator='-' * 30,
#                                            enabled_status=f'🟩 {Localization().gettext("confirmation_yes")}'
#                                            if user.status == "active"
#                                            else f'🟥 {Localization().gettext("confirmation_no")}',
#                                            tg_id=tg_id,
#                                            email=user_id,  # Marzban uses username as identifier
#                                            down_mb=bytes_to_mb(total_used_traffic),
#                                            up_mb=0,  # Marzban doesn't split up/down traffic
#                                            traffic_left=bytes_to_gb(traffic_left),
#                                            time_left=format_time_difference(user.expire * 1000) if user.expire else 0,
#                                            subscription=await self.generate_subscription_link(user_id))
#             return result
#         except Exception as e:
#             logging.error(f"Error fetching account [{user_id}]: {e}")
#             return Localization().gettext("error_default", error_id=str(uuid.uuid4())[:8])
#
#     async def check_user_status(self, user_id, tg_id):
#         try:
#             user = await self.panel.get_user(user_username=user_id, token=self.token)
#             if not user:
#                 return Localization().gettext("error_user_not_found"), None
#
#             if user.status != "active":
#                 return Localization().gettext("error_vpn_deactivated"), None
#
#             if user.expire and datetime.fromtimestamp(user.expire) < datetime.now():
#                 return Localization().gettext("error_vpn_expired"), None
#
#             usage = await self.panel.get_user_usage(user_username=user_id, token=self.token)
#             total_used_traffic = sum(node['used_traffic'] for node in usage)
#             if user.data_limit and total_used_traffic > user.data_limit:
#                 return Localization().gettext("error_traffic_exceeded"), None
#
#             return user, None
#         except Exception as e:
#             logging.error(f"Error checking user status [{user_id}]: {e}")
#             return Localization().gettext("error_default", error_id=str(uuid.uuid4())[:8]), None
#
#     async def check_traffic_left(self, tg_id):
#         try:
#             user = await self.panel.get_user(user_username=str(tg_id), token=self.token)
#             if not user:
#                 return 0
#             usage = await self.panel.get_user_usage(user_username=str(tg_id), token=self.token)
#             total_used_traffic = sum(node['used_traffic'] for node in usage)
#             return user.data_limit - total_used_traffic if user.data_limit else 0
#         except Exception as e:
#             logging.error(f"Error checking traffic left [{tg_id}]: {e}")
#             return 0