from aiogram.dispatcher.filters.state import StatesGroup, State


class NewUser(StatesGroup):
    state_new_user = State()

    #Все что может быть связано с преподавателем
    state_teacher = State()
    state_teacher_add = State()
    state_teacher_get_code = State()
    state_teacher_add_new_group = State()
    state_teacher_add_group_day = State()
    state_teacher_add_group_course = State()
    state_teacher_add_last_lesson = State()
    #все что может быть связано с учеником
    state_student_add_name = State()

