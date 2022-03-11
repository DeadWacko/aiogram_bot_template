import random
import re
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import callback_query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import NoneType
from app.db_api.models import User, Teacher, Group, student_group, Student
from app.keyboards.inline import choice
from app.keyboards.inline.first_choise import jedi_menu_keyboard_markup
from app.states import NewUser
import smtplib, ssl


def send_mail(autorization_pin: int, user_mail: str) -> None:
    smtp_server = "smtp.gmail.com"
    port = 587
    password = "12e131313"
    email_sender = "my@gmail.com"
    message = "Привет"


    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(password=password, user=email_sender)
        server.send_mail()
    except:
        print("Произошла ошибка")
    finally:
        server.quit()


def parser(input_data: str) -> list:
    """ Функция парсит строку 'текущий курс' из бэка. возвращает список из 8 элементов
    название курса, id курса, год курса, возраст учеников, время занятий, язык курса, его актуальность"""

    try:
        input_data = input_data.split(" ")
        test_str_2 = ""
        test_list = []
        for i in input_data:
            if "[" in i and "]" in i:
                test_list.append(i)
            else:
                test_str_2 += i + " "
        answer = []
        answer.append(test_str_2)
        answer.append(test_list.pop(0).replace("]", "").replace("[", ""))
        pars_data = test_list[0].replace("[", '').split("]")
        answer.append(pars_data[0])
        answer.append(pars_data[1])
        answer.append(pars_data[2])
        answer.append(pars_data[3])
        answer.append(pars_data[4])
        answer.append(pars_data[5])
        return answer
    except:
        return False


########################################################################################################################

# # Добавление студента по ссылке
# async def adding_student_by_link(message: types.Message, state: FSMContext, db: AsyncSession):
#     group_name = message.get_args()
#     await message.answer(f"Привет, сейчас поищу твою группу: {group_name}")
#     db_group = await db.execute(select(Group).where(Group.group_name == group_name))
#     data = db_group.scalars().all()
#     test_group = Group()
#     test_group.group_name = "TEST"
#     db.add(test_group)
#     await db.commit()
#
#     # Так же нужно написать добавление студента, ибо как ему иначе жить
#     if len(data) != 0:
#         await message.answer("Шикарно, я нашел твою группу, теперь введи свое имя и фамилию и дело в шляпе:3")
#         async with state.proxy() as data:
#             data["group_id"] = group_name
#         await NewUser.state_student_add_name.set()
#     else:
#         await message.answer("Ой, твоей группы в базе нет((\n Напиши своему преподавателю..")
#
#
# # добавление имени студента
# async def student_add_name(message: types.Message, state: FSMContext, db: AsyncSession):
#     full_name = message.text  # Получаем его имя
#
#     async with state.proxy() as data:
#         group_id = data["group_id"]  # Получаем группу, в которую он захотел добавиться
#
#         # TODO:
#         #    ищем ученика в списке юзеров, если его нет - добавляем его в общий список и  в группу учеников
#         #   если он есть - проверяем есть ли он в какой-либо группе(если есть - выводим его группу и спрашиваем у него, хочет ли он добавиться еще в одну группу)
#         #                                                       (если он хочет добавиться в новую группу -    добавляем его в новую группу)
#         #   говорим что все получилось и заканчиваем на этом
########################################################################################################################
"""Работа с преподавателем. Добавление его в бд, со всем следующим функционалом"""


# просим препода ввести почту
async def teacher_get_email(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession):
    await NewUser.state_teacher_add.set()
    data = await db.get(User, callback.from_user.id)
    await callback.answer(f"{data}")
    if type(data) != NoneType:
        await callback.message.answer("ТЫ УЖЕ ЕСТЬ ТУТЬ, ПОЭТОМУ ПОШЕЛ К ЧЕРТУ")
    else:
        async with state.proxy() as data:
            data["num"] = 3
            await callback.message.answer(
                f"Окей, введи свою корпоративную почту. у тебя будет {data['num']} попыток ")

    # отправляем на почту преподавателя код


# хватаем почту и отправляем на нее отправляем код
async def teacher_send_code_to_email(message: types.Message, db: AsyncSession, state: FSMContext):
    mail = message.text
    await message.answer(text=f"Отправил код на почту {mail}")
    # Кидаем код на почту с правильным доменом, в противном случае шлем подальше
    #
    #
    code = random.randint(10000, 100000)
    await message.answer(text=f"твой код: {code}")
    async with state.proxy() as data:
        data["email_code"] = code
    await NewUser.state_teacher_get_code.set()


# хватаем код который ввел преподаватель и проверяем его. если подошел - прекрасно. если нет - в жопу его
async def teacher_teacher_get_code(message: types.Message, db: AsyncSession, state: FSMContext):
    code = message.text
    await message.answer(text=f"Ты прислал код {code}. Проверяем")
    async with state.proxy() as data:
        if data["email_code"] == int(code):
            await message.answer(text=f"Код подошел, добавляю тебя в базу данных!")
            data = await db.get(User, message.from_user.id)
            if type(data) != NoneType:
                await message.answer("Ты уже у меня был, лови меню:", reply_markup=jedi_menu_keyboard_markup)
                await state.reset_state(with_data=False)
            else:
                # добавляем преподавателя
                new_user = User(telegram_id=message.from_user.id)
                new_teacher = Teacher()
                new_user.teacher = new_teacher
                db.add(new_user)
                await db.commit()
                await message.answer("Добавлен, лови меню", reply_markup=jedi_menu_keyboard_markup)
                await state.reset_state(with_data=False)
        else:
            await message.answer(text="Ошибочка")


########################################################################################################################
"""Работа с группами. Добавление, установка напоминаний и вся первоначальная настройка"""


# Добавление новой группы ++++++++++
async def teacher_add_new_group(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession):
    await NewUser.state_teacher_add_new_group.set()
    # await callback.message.edit_text(text=" ")
    await callback.message.answer(text="Введи имя группы как в бэке")


# запоминаем имя группы
async def get_group_name(message: types.Message, db: AsyncSession, state: FSMContext):
    async with state.proxy() as data:
        data["group_name"] = message.text
    await message.answer(text="Теперь введи номер последнего урока в формате М1У1")
    await NewUser.state_teacher_add_last_lesson.set()  # кидаем в следующее состояние


# запоминаем номер последнего урока
async def get_group_last_lesson(message: types.Message, db: AsyncSession, state: FSMContext):
    async with state.proxy() as data:
        data["last_lesson"] = message.text
    await message.answer(text="В какой день недели у вас занятие? пример: Пн,Вт,Ср,Чт,Пт,Сб,Вс")
    await NewUser.state_teacher_add_group_day.set()  # кидаем в следующее состояние


# Просим ввести день недели
async def get_group_weekday(message: types.Message, db: AsyncSession, state: FSMContext):
    async with state.proxy() as data:
        data["weekday"] = message.text
    await message.answer(
        text="И последнее. Введи название курса как в бэке. Пример: [186] Python базовый Kids [2021][12-15][50m,90m][32L][Ru][Actual]")
    await NewUser.state_teacher_add_group_course.set()  # кидаем в следующее состояние


# Просим ввести время урока


# Просим ввести название курса как в бэке : Пример: 	[186] Python базовый Kids [2021][12-15][50m,90m][32L][Ru][Actual]
#                                                    [номер курса] Название курса [год курса][возраст учеников][время урока][количество уроков][язык курса][актуальность курса]

async def get_group_course(message: types.Message, db: AsyncSession, state: FSMContext):
    result = parser(message.text)
    if type(result) != bool:
        async with state.proxy() as data:
            data["group_course"] = message.text
        await message.answer(text=f'Давай посмотрим что ты ввел:\n'
                                  f'Имя группы: {data["group_name"]}\n'
                                  f'Название курса {result[0]}\n'
                                  f'id курса: {result[0]}\n'
                                  f'Последний урок: {data["last_lesson"]}\n'
                                  f'год курса: {data["last_lesson"]} - по настоящее время\n'
                                  f'||Все верно?||')
    else:
        await message.answer(text='Введите как в бэке, пожалуйста, это не верно')


########################################################################################################################
# НЕ НУЖДАЕТСЯ В ИСПРАВЛЕНИЯХ в теории


# если почта преподавателя неправильная - говорим ему что он плохой ✅✅✅✅✅✅
async def answer_on_bad_mail(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["num"] -= 1
        if data['num'] != 0:
            await message.answer(text=f"Ты крутой, но увы, почта не подходит. у тебя еще {data['num']} попытки")
        else:
            await message.answer(text="так, ты меня достал, брысь обратно", reply_markup=choice)
            await NewUser.state_new_user.set()


# кнопка старт ✅✅✅
async def start(message: types.Message, db: AsyncSession):
    data = await db.get(User, message.from_user.id)

    if type(data) != NoneType:
        await message.answer(f"Так,ты уже есть. проверяю кто ты")
        print(data.teacher_id)
        print(data.student_id)
        if data.teacher_id != None:
            await message.answer(" лови меню", reply_markup=jedi_menu_keyboard_markup)
        elif data.student_id != None:
            await message.answer("Господин cтудент, ловите функционал")
        else:
            print("ERROR")
        print(data.student_id)

    else:
        await message.answer(f"Привет, давай определимся кто ты такой", reply_markup=choice)
        await NewUser.state_new_user.set()


########################################################################################################################
def register_start(dp: Dispatcher):
    # dp.register_message_handler(adding_student_by_link,
    #                            CommandStart(deep_link=re.compile(r"^[A-Z]{4,15}$")))
    dp.register_message_handler(start, CommandStart())
    # dp.register_message_handler(student_add_name, state=NewUser.state_student_add_name)
    dp.register_callback_query_handler(teacher_get_email, text="teacher", state=NewUser.state_new_user)
    dp.register_message_handler(teacher_send_code_to_email, Text(endswith="@kodland.team"),
                                state=NewUser.state_teacher_add)
    dp.register_message_handler(teacher_teacher_get_code, state=NewUser.state_teacher_get_code)
    dp.register_message_handler(answer_on_bad_mail, state=NewUser.state_teacher_add)
    dp.register_callback_query_handler(teacher_add_new_group, text="event_add_group_button")  # +
    dp.register_message_handler(get_group_name, state=NewUser.state_teacher_add_new_group)  # +
    dp.register_message_handler(get_group_last_lesson, state=NewUser.state_teacher_add_last_lesson)
    dp.register_message_handler(get_group_weekday, state=NewUser.state_teacher_add_group_day)
    dp.register_message_handler(get_group_course, state=NewUser.state_teacher_add_group_course)
