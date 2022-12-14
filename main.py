import os
from datetime import date

import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from progress import Progress
from projectCode import ProjectCode

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

# constants
DESIGN = 1
DRAFTING = 2
RENDERING = 3

SINGAPORE_CODE = 65
CAMBODIA_CODE = 855

# dictionary to keep track of chat progress
chat_progresses: [Progress, ProjectCode] = {}


def add_to_progress(chat_id):
    chat_progresses[chat_id] = [Progress.STEP_1, ProjectCode()]
    print(chat_progresses)


def update_progress(chat_id, updated_progress):
    chat_progresses[chat_id][0] = updated_progress


def delete_progress(chat_id):
    del chat_progresses[chat_id][1]
    del chat_progresses[chat_id]
    print(chat_progresses)


def get_progress(chat_id):
    return chat_progresses[chat_id][0]


def get_project_code(chat_id) -> ProjectCode:
    return chat_progresses[chat_id][1]


# -----------------------------------------------


def markup_inline_step_1():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(types.InlineKeyboardButton("Design - 1", callback_data=DESIGN))
    markup.add(types.InlineKeyboardButton("Drafting - 2", callback_data=DRAFTING))
    markup.add(types.InlineKeyboardButton("Rendering - 3", callback_data=RENDERING))
    return markup


def markup_inline_step_3():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(types.InlineKeyboardButton("Singapore(SG) - 65", callback_data=SINGAPORE_CODE))
    markup.add(types.InlineKeyboardButton("Cambodia(KH) - 855", callback_data=CAMBODIA_CODE))
    return markup


@bot.message_handler(commands=['new_project'])
def new_project(message):
    chat_id = message.chat.id
    if chat_id in chat_progresses:
        bot.send_message(chat_id, "There is already a project in progress")
    else:
        add_to_progress(chat_id)
        bot.send_message(chat_id, "Select the nature of the project", reply_markup=markup_inline_step_1())


@bot.message_handler(commands=['cancel'])
def cancel(message):
    chat_id = message.chat.id
    if chat_id in chat_progresses:
        delete_progress(chat_id)
        bot.send_message(chat_id, "Project deleted")
    else:
        bot.send_message(chat_id, "No project in progress")


def display_updated_project_code(chat_id):
    bot.send_message(chat_id, "Current project code: " + str(get_project_code(chat_id)))


def display_project_details(chat_id):
    bot.send_message(chat_id, get_project_code(chat_id).get_details())


def update_project_nature_code(chat_id, nature: int):
    chat_progresses[chat_id][1].set_nature_code(nature)


def update_project_date(chat_id, d: date):
    chat_progresses[chat_id][1].set_date(d)


def update_project_country_code(chat_id, country: int):
    chat_progresses[chat_id][1].set_country_code(country)


def update_project_name(chat_id, name: str):
    chat_progresses[chat_id][1].set_name(name)


def process_step_1(call):
    chat_id = call.message.chat.id

    update_project_nature_code(chat_id, call.data)
    bot.answer_callback_query(call.id, "Updated")

    bot.edit_message_text(f"You selected {call.data}", chat_id, call.message.message_id)
    display_updated_project_code(chat_id)

    update_progress(chat_id, Progress.STEP_2)

    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(chat_id, "Select the date of the project opening", reply_markup=calendar)


def process_step_2(call):
    chat_id = call.message.chat.id
    result, key, step = DetailedTelegramCalendar().process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              chat_id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        reformatted_date = result.strftime("%d/%m/%y")
        bot.edit_message_text(f"You selected {reformatted_date}",
                              chat_id,
                              call.message.message_id)

        update_project_date(chat_id, result)
        display_updated_project_code(chat_id)

        update_progress(chat_id, Progress.STEP_3)

        bot.send_message(chat_id, "Select the project location (country code)", reply_markup=markup_inline_step_3())


def process_step_3(call):
    chat_id = call.message.chat.id

    update_project_country_code(chat_id, call.data)
    bot.answer_callback_query(call.id, "Updated")

    bot.edit_message_text(f"You selected {call.data}", chat_id, call.message.message_id)
    display_updated_project_code(chat_id)

    update_progress(chat_id, Progress.STEP_4)
    bot.send_message(chat_id, "Please enter the project's name/address")


def process_step_4(message):
    chat_id = message.chat.id
    update_project_name(chat_id, message.text)

    bot.send_message(chat_id, f"Your project's name is: {message.text}")
    display_updated_project_code(chat_id)
    display_project_details(chat_id)


@bot.callback_query_handler(func=lambda message: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in chat_progresses:
        bot.answer_callback_query(call.id, "Please start a new project first")
        return

    current_progress = get_progress(chat_id)
    if current_progress == Progress.STEP_1:
        process_step_1(call)
    elif current_progress == Progress.STEP_2:
        process_step_2(call)
    elif current_progress == Progress.STEP_3:
        process_step_3(call)
    else:
        pass


@bot.message_handler(func=lambda message: True)
def handle_text_doc(message):
    chat_id = message.chat.id
    if chat_id not in chat_progresses:
        return

    current_progress = get_progress(chat_id)
    if current_progress == Progress.STEP_4:
        process_step_4(message)


bot.infinity_polling()
