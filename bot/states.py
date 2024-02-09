from aiogram.fsm.state import State, StatesGroup


class Navigation(StatesGroup):
    main_menu = State()


class Form(StatesGroup):
    choosing_job_site = State()
    input_occupation = State()
    input_location = State()
    choosing_experience = State()
    choosing_employment_type = State()
    choosing_salary_from = State()
    choosing_salary_to = State()
    confirm_operation = State()
