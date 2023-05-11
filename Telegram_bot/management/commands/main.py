import telebot
import requests
import json

from telebot import types

from Telegram_bot.models import Users
from Telegram_bot.models import Courses
from Basic.settings import BOT_TOKEN, MOODLE_URL, MOODLE_TOKEN

print('mainstart')

bot = telebot.TeleBot(BOT_TOKEN)

get_course_url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json"
get_course_response = requests.get(get_course_url)
all_courses = json.loads(get_course_response.text)
for course_init in all_courses:
    course_i, created = Courses.objects.get_or_create(id_course=course_init['id'], short_name=course_init['shortname'], full_name=course_init['fullname'])


@bot.message_handler(commands=['getfaq'])
def get_courses(message):
    print('get_courses_activate')
    user = Users.objects.get(id_tg=message.chat.id)
    id_moodle = user.id_moodle
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&wsfunction=core_enrol_get_users_courses&userid={id_moodle}&moodlewsrestformat=json"
    response = requests.get(url)
    courses = json.loads(response.text)
    markup = types.InlineKeyboardMarkup()
    if not courses:
        bot.send_message(message.chat.id, "вы не записаны ни на один курс")
    else:
        text = ""
        for course in courses:
            course_name = f"{course['fullname']}"
            button1 = types.InlineKeyboardButton(text=course_name, callback_data=course_name, resize_keyboard=True)
            markup.add(button1)
            text += f"{course['fullname']} ({course['shortname']} {course['id']})\n"
        bot.send_message(message.chat.id, "Курсы на которые вы записаны: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def info(call):
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&moodlewsrestformat=json&wsfunction=get_telegrambotcontent&id=4"
    response = requests.get(url)
    course_id = Courses.objects.get(full_name=call.data).id_course
    courses = json.loads(response.text)
    text = ''
    for course in reversed(courses):
        if int(course['course']) == course_id:
            structure = json.loads(course.get('structure'))
            for content in structure.values():
                question = content.get('name')
                answer = content.get('answer')
                text += f"{question}" + " " + f"{answer}" + "\n"
            break
    bot.send_message(call.message.chat.id, text)


@bot.message_handler(commands=['start'])
def start(message):
    print('start_activate')
    username = message.from_user.username
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&wsfunction=get_user_by_field_tg&username_tg={username}&moodlewsrestformat=json"
    response = requests.get(url)
    id_moodle = json.loads(response.text)
    if (id_moodle == None):
        bot.send_message(message.chat.id, 'вы не записали свой username')
    else:
        id_moodle = json.loads(response.text)
        user, created = Users.objects.get_or_create(id_tg=message.chat.id, defaults={'id_moodle': id_moodle})
        if (not created):
            bot.send_message(message.chat.id, "вы уже записаны в базу бота")
            bot.send_message(message.chat.id, f"{user.id_tg} {user.id_moodle}")
        else:
            bot.send_message(message.chat.id, "вac записали в базу бота")
            bot.send_message(message.chat.id, f"{user.id_tg} {user.id_moodle}")


bot.polling(none_stop=True)
