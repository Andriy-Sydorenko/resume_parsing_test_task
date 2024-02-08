import asyncio
import logging
import os
import sys

import utils
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

from scraping.main import parse_resumes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

FILTERS = {
    "job_position": "продавець",
    "location": "Київ",
    "work_experience": "Up to 1 year",
    "employment_type": "Full time",
    "salary_from": 2000,
    "salary_to": 10000
}


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    # Greet the user
    await message.answer("Hello! I'm your resume search assistant. "
                         "Use the menu to start searching for resumes.")

    # Define reply keyboard
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [
            KeyboardButton(text="Start Searching for Resumes"),
        ]
    ], )

    # Send a message with the keyboard
    await message.answer("Choose an option:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "Start Searching for Resumes")
async def start_search(message: types.Message):
    await message.answer("Started searching for resumes...")
    list_of_resumes, total_resume_count, warning = await parse_resumes(FILTERS)
    await utils.send_list_of_dicts_as_message(message=message,
                                              list_of_dicts=list_of_resumes,
                                              total_resume_count=total_resume_count)
    if warning:
        await message.answer(warning)


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
