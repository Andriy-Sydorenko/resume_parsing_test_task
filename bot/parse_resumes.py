from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import bot, utils
from bot.states import Form, Navigation
from scraping import main, scrapers

search_router = Router()

PARSERS = {
    "work.ua": scrapers.WorkUaScraper,
    "robota.ua": scrapers.RobotaUaScraper,
}


@search_router.message(lambda message: message.text == "Start Searching for Resumes")
async def start_process(message: types.Message, state: FSMContext):
    job_site_keyboard = utils.create_formatted_inline_keyboard(["work.ua", "robota.ua"])

    bot_message = await message.answer("Choose a job site:", reply_markup=job_site_keyboard)
    await state.update_data(bot_message_id=bot_message.message_id)
    await state.set_state(Form.choosing_job_site)


@search_router.callback_query(Form.choosing_job_site)
async def process_job_site_selection(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(job_site=callback_query.data)
    await callback_query.message.edit_text(
        text=f"You've selected {callback_query.data}.\n\nPlease enter the occupation:",
        reply_markup=None,
    )
    await state.set_state(Form.input_occupation)


@search_router.message(Form.input_occupation)
async def process_occupation(message: types.Message, state: FSMContext):
    await state.update_data(job_position=message.text)
    state_memo = await state.get_data()
    bot_message_id = state_memo.get("bot_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text="Please enter the city:",
    )
    await state.set_state(Form.input_location)


@search_router.message(Form.input_location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    state_memo = await state.get_data()
    parser_class = PARSERS.get(state_memo.get("job_site"))

    experience_keyboard = utils.create_formatted_inline_keyboard(parser_class.work_experience.keys())

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=state_memo.get("bot_message_id"),
        text="Please choose the experience level:",
        reply_markup=experience_keyboard,
    )
    await state.set_state(Form.choosing_experience)


@search_router.callback_query(Form.choosing_experience)
async def process_experience(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(work_experience=callback_query.data)
    state_memo = await state.get_data()
    parser_class = PARSERS.get(state_memo.get("job_site"))
    employment_type_keyboard = utils.create_formatted_inline_keyboard(parser_class.employment_type.keys())

    await callback_query.message.edit_text(
        text="Choose employment type",
        reply_markup=employment_type_keyboard,
    )
    await state.set_state(Form.choosing_employment_type)


@search_router.callback_query(Form.choosing_employment_type)
async def process_employment_type(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(employment_type=callback_query.data)
    state_memo = await state.get_data()
    parser_class = PARSERS.get(state_memo.get("job_site"))
    salaries = [str(salary) for salary in parser_class.salaries.keys()]
    salary_from_keyboard = utils.create_formatted_inline_keyboard(salaries)

    await callback_query.message.edit_text(
        text="Choose minimum salary: ",
        reply_markup=salary_from_keyboard,
    )
    await state.set_state(Form.choosing_salary_from)


@search_router.callback_query(Form.choosing_salary_from)
async def process_salary_from(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(salary_from=int(callback_query.data))
    state_memo = await state.get_data()
    parser_class = PARSERS.get(state_memo.get("job_site"))

    salaries = [str(salary) for salary in list(parser_class.salaries.keys())[1:]]
    salary_to_keyboard = utils.create_formatted_inline_keyboard(salaries)

    await callback_query.message.edit_text(
        text="Choose maximum salary: ",
        reply_markup=salary_to_keyboard,
    )
    await state.set_state(Form.choosing_salary_to)


@search_router.callback_query(Form.choosing_salary_to)
async def find_resumes(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(salary_to=int(callback_query.data))
    state_memo = await state.get_data()
    confirm_operation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Confirm operation", callback_data="confirm_operation"),
            InlineKeyboardButton(text="Cancel operation", callback_data="cancel_operation"),
        ]
    ], )

    await callback_query.message.edit_text(
        text=(f"So, final filters: \n"
              f"*Position:* {state_memo.get('job_position')}\n"
              f"*City:* {state_memo.get('location')}\n"
              f"*Work experience:* {state_memo.get('work_experience')}\n"
              f"*Employment type:* {state_memo.get('employment_type')}\n"
              f"*Minimum salary:* {state_memo.get('salary_from')}\n"
              f"*Maximum salary:* {state_memo.get('salary_to')}\n\n"
              f"*Do you want to start search?*"),
        reply_markup=confirm_operation_keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(Form.confirm_operation)


@search_router.callback_query(Form.confirm_operation)
async def confirm_and_execute_operation(callback_query: types.CallbackQuery, state: FSMContext):
    callback_data = callback_query.data
    if callback_data == "confirm_operation":
        state_memo = await state.get_data()
        filters = {
            "job_position": state_memo.get("job_position"),
            "location": state_memo.get("location"),
            "work_experience": state_memo.get("work_experience"),
            "employment_type": state_memo.get("employment_type"),
            "salary_from": state_memo.get("salary_from"),
            "salary_to": state_memo.get("salary_to"),
        }
        parser_class = PARSERS.get(state_memo.get("job_site"))
        list_of_resumes, total_resume_count, warning = await main.parse_resumes(filters=filters,
                                                                                parser_class=parser_class)
        await utils.send_message_with_resumes(
            callback_query=callback_query,
            list_of_dicts=list_of_resumes,
            total_resume_count=total_resume_count,
            warning=warning
        )

    await state.set_state(Navigation.main_menu)
    # TODO: main menu doesn't work, maybe the problem is in router
