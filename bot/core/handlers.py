from aiogram import Router, types, F
from aiogram.filters import Command
from .api_client import api_client, UserNotFoundError

# from .keyboards import ... # импорт клавиатур

router = Router()


@router.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer("Добро пожаловать! Нажмите 'Личный кабинет', чтобы увидеть информацию о подписке.")


@router.message(F.text == "Личный кабинет")  # Предположим, у тебя есть такая кнопка
async def handle_personal_cabinet(message: types.Message):
    telegram_id = message.from_user.id

    try:
        # 1. Делаем всего один запрос к нашему API
        profile_data = await api_client.get_profile(telegram_id)

        # 2. Форматируем красивый ответ из полученных данных
        user_info = profile_data.get('user', {})
        subscription_info = profile_data.get('active_subscription')

        full_name = user_info.get('full_name', 'Без имени')
        email = user_info.get('email', 'Не указан')

        text_lines = [
            f"👤 *Профиль: {full_name}*",
            f"✉️ Email: `{email}`",
        ]

        if subscription_info:
            plan_info = subscription_info.get('plan') or {}
            plan_name = plan_info.get('name', 'N/A')
            end_date = subscription_info.get('end_date', 'N/A')
            sub_url = user_info.get('subscription_url', 'Отсутствует')

            text_lines.extend([
                "\n✅ *Активная подписка*",
                f"🏷️ Тариф: *{plan_name}*",
                f"🗓️ Действует до: `{end_date}`",
                "\n🔗 Ваша ссылка для подключения:",
                f"`{sub_url}`"
            ])
        else:
            text_lines.append("\n❌ *У вас нет активной подписки*")

        await message.answer("\n".join(text_lines), parse_mode="Markdown")

    except UserNotFoundError:
        await message.answer(
            "Вы еще не зарегистрированы. Пожалуйста, пройдите регистрацию на нашем сайте или используйте команду /start с реферальным кодом.")
    except Exception as e:
        print(f"Error in personal cabinet handler: {e}")  # Логирование
        await message.answer("Произошла ошибка при получении данных. Пожалуйста, попробуйте позже.")


@router.message(F.text == "Тест")  # Или callback_query
async def handle_test_vpn(message: types.Message):
    user = message.from_user

    try:
        await message.answer("У вас уже есть аккаунт. Вот информация о нем:")
        await handle_personal_cabinet(message) # <-- ВЫЗЫВАЕМ ДРУГОЙ ХЕНДЛЕР

    except UserNotFoundError:
        # Ага, пользователя нет! Регистрируем его.
        try:
            await message.answer("Похоже, вы у нас впервые! Создаю для вас пробный доступ...")

            registration_result = await api_client.register_trial(
                telegram_id=user.id,
                full_name=user.full_name,
                username=user.username
            )

            # Форматируем красивое приветственное сообщение из результата
            sub_url = registration_result.get("subscription", {}).get("user", {}).get("subscription_url")
            end_date = registration_result.get("subscription", {}).get("end_date")

            await message.answer(
                f"Готово! ✅\n\nВам выдан пробный доступ до {end_date}.\n\n"
                f"Ваша ссылка для подключения:\n`{sub_url}`",
                parse_mode="Markdown"
            )
        except Exception as e:
            await message.answer(f"Не удалось создать пробный доступ: {e}")

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")