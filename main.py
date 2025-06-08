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
    text = ("""
        Здравствуйте! 👋

        Я ассистент от [Токеон](https://tokeon.ru/), обученный помогать с вопросами о цифровых активах и их создании.

        Я могу помочь вам:
        * Разобраться в создании и управлении цифровыми активами
        * Понять, как работают токены и смарт-контракты
        * Оценить эффективность ваших активов
        * Найти оптимальные решения для ваших задач
        * Объяснить технические аспекты простым языком

        Задавайте любые вопросы - я помогу разобраться в теме и найти подходящие решения.

        Для начала работы просто напишите ваш вопрос в чате ниже.
    """
    )
    await message.answer(text)


async def send_to_api(question: str) -> dict:
    async with httpx.AsyncClient(base_url=API_URL) as client:
        try:
            response = await client.get(
                "/ask",
                params={"question": question}
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

    await message.answer(response["answer"])

async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())