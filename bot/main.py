import asyncio
import logging
import os
from urllib.parse import urlencode

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:3000/app")

router = Router()
setup_state: dict[int, dict[str, str]] = {}


CLIENT_TYPE_LABELS = {
    "physical_person": "Физлицо",
    "individual_entrepreneur": "ИП",
    "legal_entity": "Юрлицо",
}

DEAL_DIRECTION_LABELS = {
    "cfa": "ЦФА",
    "crypto": "Крипта",
    "cars": "Авто",
    "ved": "ВЭД",
    "other": "Другое",
}

RATE_MODE_LABELS = {
    "skip": "Указать позже",
    "no_rate": "Без ставки",
    "default": "Использовать ставку по умолчанию",
    "set_later_in_admin": "Открыть в админке",
}

REFERRAL_MODE_LABELS = {
    "no_referral": "Без реферала",
    "client_default": "Закреплен за клиентом",
    "deal_only": "Только эта сделка",
    "choose_later_in_admin": "Выбрать позже в админке",
}


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


def setup_keyboard(step: str) -> InlineKeyboardMarkup:
    options = {
        "client_type": CLIENT_TYPE_LABELS,
        "deal_direction": DEAL_DIRECTION_LABELS,
        "rate_mode": RATE_MODE_LABELS,
        "referral_mode": REFERRAL_MODE_LABELS,
    }[step]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"setup:{step}:{value}")]
            for value, label in options.items()
        ]
    )


def resolve_document_flow_type(client_type: str, deal_direction: str) -> str:
    mapping = {
        ("physical_person", "crypto"): "agency_contract_crypto_physical",
        ("individual_entrepreneur", "crypto"): "agency_contract_crypto_ie",
        ("legal_entity", "crypto"): "agency_contract_crypto_legal",
        ("physical_person", "cars"): "agency_contract_cars_physical",
        ("legal_entity", "cars"): "agency_contract_cars_legal",
        ("physical_person", "cfa"): "offer_join_statement",
        ("individual_entrepreneur", "cfa"): "agency_contract_cfa_ie",
        ("legal_entity", "cfa"): "agency_contract_cfa_legal",
        ("physical_person", "ved"): "ved_contract_physical",
        ("individual_entrepreneur", "ved"): "ved_contract_ie",
        ("legal_entity", "ved"): "ved_contract_legal",
    }
    return mapping.get((client_type, deal_direction), "custom_manual")


def template_hint(flow_type: str) -> str:
    hints = {
        "offer_join_statement": "Заявление о присоединении к оферте",
        "agency_contract_crypto_physical": "Агентский договор RSI под крипту для физика",
        "agency_contract_crypto_ie": "Агентский договор RSI под крипту для ИП",
        "agency_contract_crypto_legal": "Агентский договор RSI под крипту для юрлица",
        "agency_contract_cars_physical": "Агентский договор RSI под авто для физика",
        "agency_contract_cars_legal": "Агентский договор RSI под авто для юрлица",
    }
    return hints.get(flow_type, "Ручной подбор шаблона в админке")


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


@router.message(Command("new_document_request"))
async def new_document_request(message: Message) -> None:
    params = {"source": "bot"}
    if message.from_user:
        params["tg_id"] = str(message.from_user.id)
        if message.from_user.username:
            params["username"] = message.from_user.username
    url = f"{WEBAPP_URL.rstrip('/')}/document-request?{urlencode(params)}"
    await message.answer(f"Форма заявки на подготовку документов:\n{url}")


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
        "Чтобы клиент получил правильную форму и документы, настройте параметры сделки.\n\n"
        "Шаг 1: выберите тип клиента.",
        reply_markup=setup_keyboard("client_type"),
    )


@router.callback_query(F.data.startswith("setup:"))
async def setup_callback(callback: CallbackQuery) -> None:
    if not callback.message:
        await callback.answer()
        return

    _, step, value = callback.data.split(":", 2)
    chat_id = callback.message.chat.id
    state = setup_state.setdefault(chat_id, {})
    state[step] = value

    if step == "client_type":
        await callback.message.edit_text("Шаг 2: выберите тип сделки.", reply_markup=setup_keyboard("deal_direction"))
    elif step == "deal_direction":
        await callback.message.edit_text("Шаг 3: ставка / комиссия.", reply_markup=setup_keyboard("rate_mode"))
    elif step == "rate_mode":
        await callback.message.edit_text("Шаг 4: реферал.", reply_markup=setup_keyboard("referral_mode"))
    elif step == "referral_mode":
        client_type = state.get("client_type", "physical_person")
        deal_direction = state.get("deal_direction", "cfa")
        flow_type = resolve_document_flow_type(client_type, deal_direction)
        await callback.message.edit_text(
            "Настройка сохранена.\n"
            f"Тип клиента: {CLIENT_TYPE_LABELS.get(client_type, client_type)}.\n"
            f"Тип сделки: {DEAL_DIRECTION_LABELS.get(deal_direction, deal_direction)}.\n"
            "Форма Mini App будет адаптирована под клиента.\n"
            f"Документы: {template_hint(flow_type)}.\n"
            "Клиент может открыть Mini App и заполнить данные."
        )
    await callback.answer()


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
