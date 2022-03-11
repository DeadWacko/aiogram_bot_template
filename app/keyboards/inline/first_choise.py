from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

choice = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Преподаватель",
            callback_data="teacher"
        )
    ],
    [
        InlineKeyboardButton(
            text="ученик",
            callback_data="student"
        )
    ]
])


add_group_button = InlineKeyboardButton('Добавить группу ➕', callback_data='event_add_group_button')
show_stats_button = InlineKeyboardButton('Посмотреть статистику 📄 ', callback_data='event_show_stats_button')
mailing_button = InlineKeyboardButton('Отправить рассылку 📬 ', callback_data='event_mailing_button')
jedi_menu_keyboard_markup = InlineKeyboardMarkup().add(add_group_button).add(show_stats_button).add(mailing_button)