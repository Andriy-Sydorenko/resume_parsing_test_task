import asyncio
import logging
import sys

from aiogram import Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot import bot
from bot.parse_resumes import search_router
from bot.states import Navigation

dp = Dispatcher()


@dp.message(CommandStart())
async def send_welcome(message: types.Message, state: FSMContext):
    await message.answer("Hello! I'm your resume search assistant. "
                         "Use the menu to start searching for resumes.")

    await state.set_state(Navigation.main_menu)


@dp.message(Navigation.main_menu, Command("main_menu"))
async def main_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
        [
            KeyboardButton(text="Start Searching for Resumes"),
        ]
    ], )

    await message.answer("Choose an option:", reply_markup=keyboard)


async def main() -> None:
    dp.include_router(search_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
