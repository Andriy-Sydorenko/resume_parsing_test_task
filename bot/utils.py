from aiogram import types

from scraping.main import RESUME_DISPLAY_COUNT

MAX_MESSAGE_LENGTH = 4096


async def send_list_of_dicts_as_message(message: types.Message, list_of_dicts, total_resume_count):
    messages = []  # List to hold all message parts
    current_message = ""  # String to hold the current message part being constructed

    # Function to add the current message to the messages list and reset it
    def add_and_reset_current_message():
        nonlocal current_message
        if current_message:  # Only add if the current message is not empty
            messages.append(current_message)
            current_message = ""

    for i, dictionary in enumerate(list_of_dicts, start=1):
        # Construct the message for the current dictionary

        dict_message = "".join([f"Кандидат *{value.get('candidate_name')}*"
                                f"\n{value.get('candidate_occupation')}:"
                                f"\n{key}" for key, value in dictionary.items()]) + "\n\n"
        # Check if adding the next dictionary message would exceed the limit
        if len(current_message) + len(dict_message) > MAX_MESSAGE_LENGTH:
            add_and_reset_current_message()  # Add the current message to the list and reset it
        current_message += dict_message  # Add the dictionary message to the current message

    add_and_reset_current_message()  # Ensure the last part is added

    # Send each message part
    await message.answer(f"*A total of {total_resume_count} resumes were processed, "
                         f"and {RESUME_DISPLAY_COUNT} of them were selected*",
                         parse_mode="Markdown")
    for msg_part in messages:
        await message.answer(msg_part, parse_mode="Markdown")
