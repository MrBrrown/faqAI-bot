import asyncio
import logging

import httpx
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


TOKEN = getenv("BOT_TOKEN")
API_URL = getenv("BACKEND_URL",  default="http://localhost:8000")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    text = (
        "Привет! Я бот поддержки.\n"
        "Задайте мне вопрос о платформе, и я постараюсь помочь!"
    )
    await message.answer(text)


async def send_to_api(question: str) -> dict:
    async with httpx.AsyncClient(base_url=API_URL) as client:
        try:
            response = await client.get(
                "/ask",
                params={"question": question},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            return {"error": str(e)}


@dp.message()
async def handle_message(message: Message):
    question = message.text
    response = await send_to_api(question)

    if "error" in response:
        await message.answer("Ошибка при обработке запроса. Попробуйте позже.")
        return

    if not response.get("results"):
        await message.answer("Не нашел подходящего ответа. Попробуйте переформулировать вопрос.")
        return

    await message.answer("Service answer")


async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())