import telebot
import requests
import json
import datetime
from telebot import types

from Telegram_bot.models import Users
from Telegram_bot.models import Courses
from Basic.settings import BOT_TOKEN, MOODLE_URL, MOODLE_TOKEN

print('mainstart')

bot = telebot.TeleBot(BOT_TOKEN)

get_course_url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&wsfunction=core_course_get_courses&moodlewsrestformat=json"
get_course_response = requests.get(get_course_url)
all_courses = json.loads(get_course_response.text)
# for course_init in all_courses:
#     course_i, created = Courses.objects.get_or_create(id_course=course_init['id'], short_name=course_init['shortname'], full_name=course_init['fullname'])


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
            button1 = types.InlineKeyboardButton(text=course_name, callback_data=f"for_faq {course_name}", resize_keyboard=True)
            markup.add(button1)
            text += f"{course['fullname']} ({course['shortname']} {course['id']})\n"
        bot.send_message(message.chat.id, "Курсы на которые вы записаны: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "for_faq")
def courses_info(call):
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&moodlewsrestformat=json&wsfunction=get_telegrambotcontent&id=4"
    response = requests.get(url)
    course_id = Courses.objects.get(full_name=call.data.replace('for_faq ', '')).id_course
    courses = json.loads(response.text)
    text = ''
    markup = types.InlineKeyboardMarkup()
    for course in reversed(courses):
        if int(course['course']) == course_id:
            structure = json.loads(course.get('structure'))
            for content in structure.values():
                question = content.get('name')
                answer = content.get('answer')
                button1 = types.InlineKeyboardButton(text=question, callback_data=f"for_answer {answer}", resize_keyboard=True)
                markup.add(button1)
                text += f"{question}" + " " + f"{answer}" + "\n"
            break
    bot.send_message(call.message.chat.id, "Выберите интересующий вас вопрос:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "for_answer")
def answers(call):
    text = call.data.replace('for_answer ', '')
    print(text)
    bot.send_message(call.message.chat.id, text)


@bot.message_handler(commands=['getdeadlines'])
def get_deadline(message):
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
            course_id = f"{course['id']}"
            button1 = types.InlineKeyboardButton(text=course_name, callback_data=f"{course_id} for_deadlines", resize_keyboard=True)
            markup.add(button1)
            text += f"{course['fullname']} ({course['shortname']} {course['id']})\n"
        bot.send_message(message.chat.id, "Курсы на которые вы записаны: ", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split()[1] == "for_deadlines")
def deadline_info(call):
    course_id = call.data.split()[0]
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&moodlewsrestformat=json&wsfunction=mod_assign_get_assignments&courseids[0]={course_id}"
    response = requests.get(url)
    contentAssigment = json.loads(response.text)
    tasks = ''
    assignments = contentAssigment["courses"][0]["assignments"]
    for assignment in assignments:
        name = assignment["name"]
        deadline = assignment["duedate"]
        if deadline == 0:
            deadline = "без дедлайна"
        elif deadline < datetime.datetime.now().timestamp():
            continue
        else:
            deadline = datetime.datetime.fromtimestamp(deadline)
        tasks += f"{name}:       {deadline} \n"
    if len(tasks) != 0:
        tasks = "задания \n" + tasks
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&moodlewsrestformat=json&wsfunction=mod_quiz_get_quizzes_by_courses&courseids[0]={course_id}"
    response = requests.get(url)
    contentQuiz = json.loads(response.text)
    quizzes = contentQuiz["quizzes"]
    tests = ''
    for quiz in quizzes:
        name = quiz["name"]
        deadline = quiz["timeclose"]
        if deadline == 0:
            deadline = "без дедлайна"
        elif deadline < datetime.datetime.now().timestamp():
            continue
        else:
            deadline = datetime.datetime.fromtimestamp(deadline)
        tests += f"{name}:       {deadline} \n"
    if len(tests) != 0:
        tests = "тесты \n" + tests
    text = tasks + tests
    if len(text) != 0:
        bot.send_message(call.message.chat.id, text)
    else:
        bot.send_message(call.message.chat.id, "заданий нет")


@bot.message_handler(commands=['start'])
def start(message):
    print('start_activate')
    username = message.from_user.username
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&wsfunction=get_user_by_field_tg&username_tg={username}&moodlewsrestformat=json"
    response = requests.get(url)
    id_moodle = json.loads(response.text)
    if (id_moodle == None):
        bot.send_message(message.chat.id, 'Вы не записали свой username:(\n\nВам нужно записать свой username телеграмма в личном кабинете образовательного портала для этого: \n1) Зайдите на портал \n2) Зайдите в "О пользователе" -> "Редактировать информацию" -> "Необязательные поля" \n3) Ввести в поле skype ID свой username телеграмма \n4) Сохранить изменения')
    else:
        id_moodle = json.loads(response.text)
        user, created = Users.objects.get_or_create(id_tg=message.chat.id, defaults={'id_moodle': id_moodle})
        if (not created):
            bot.send_message(message.chat.id, "вы уже записаны в базу бота")
            #bot.send_message(message.chat.id, f"{user.id_tg} {user.id_moodle}")
        else:
            bot.send_message(message.chat.id, "вac записали в базу бота")
            #bot.send_message(message.chat.id, f"{user.id_tg} {user.id_moodle}")


bot.polling(none_stop=True)
