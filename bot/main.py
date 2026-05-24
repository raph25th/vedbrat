import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart
from aiogram.types import ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:3000/app")

router = Router()


def is_https_webapp_url() -> bool:
    return WEBAPP_URL.startswith("https://")


def is_local_webapp_url() -> bool:
    return WEBAPP_URL.startswith("http://localhost") or WEBAPP_URL.startswith("http://127.0.0.1")


def webapp_keyboard() -> InlineKeyboardMarkup | None:
    if not is_https_webapp_url():
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть CFA Mini App",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def start(message: Message) -> None:
    text = (
        "VEDBRAT CFA bot подключен.\n"
        "Через Mini App можно заполнить профиль, реквизиты, посмотреть сделки, документы и указать кошелек."
    )
    keyboard = webapp_keyboard()

    if is_local_webapp_url():
        text += (
            "\n\nДля Telegram Mini App нужен HTTPS URL. "
            f"Сейчас WEBAPP_URL локальный: {WEBAPP_URL}\n"
            "Задайте HTTPS WEBAPP_URL через ngrok или production domain."
        )
    elif not is_https_webapp_url():
        text += "\n\nЗадайте HTTPS WEBAPP_URL через ngrok или production domain, чтобы открыть Mini App из Telegram."

    await message.answer(text, reply_markup=keyboard)


@router.my_chat_member(F.chat.type.in_({"group", "supergroup"}))
async def on_bot_added(event: ChatMemberUpdated, bot: Bot) -> None:
    added = event.new_chat_member.status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
    }
    if not added:
        return

    await bot.send_message(
        event.chat.id,
        "Бот подключен к группе.\n\n"
        "Пока работает тестовый режим без проверки прав. "
        "Дальше менеджер сможет связать группу с клиентом или агентом.",
    )


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message(message: Message) -> None:
    if message.text and message.text.startswith("/status"):
        await message.answer("Группа ожидает привязки в CFA CRM.")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
