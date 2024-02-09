from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from scraping.main import RESUME_DISPLAY_COUNT


async def send_message_with_resumes(callback_query: types.CallbackQuery,
                                    list_of_dicts,
                                    total_resume_count,
                                    warning=None):
    resumes = ""
    for resume_dict in list_of_dicts[:RESUME_DISPLAY_COUNT]:  # Limit the number of resumes displayed
        for link, info in resume_dict.items():
            resumes += (f"Кандидат: *{info.get('candidate_name')}*\n"
                        f"Occupation: *{info.get('candidate_occupation')}*\n"
                        f"Link: {link}\n\n")

    total_text = (f"*Found {total_resume_count} resumes*\n"
                  f"*Shown {RESUME_DISPLAY_COUNT}*\n\n\n") + resumes
    if warning:
        total_text += f"\n\n*{warning}*"

    print(total_text)

    await callback_query.message.answer(
        text=total_text,
        parse_mode="Markdown",
    )


def chunk_list(lst, chunk_size):
    """
    Function that is used to evenly distribute inline keyboard buttons
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def create_formatted_inline_keyboard(values: list):
    buttons = [InlineKeyboardButton(text=key, callback_data=key) for key in values]
    button_rows = list(chunk_list(buttons, chunk_size=4))
    experience_keyboard = InlineKeyboardMarkup(inline_keyboard=button_rows)
    return experience_keyboard
