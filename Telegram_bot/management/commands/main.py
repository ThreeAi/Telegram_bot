import telebot
import requests
import json
from Telegram_bot.models import Users
from Basic.settings import BOT_TOKEN, MOODLE_URL, MOODLE_TOKEN

print('mainstart')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['getcourses'])
def getcourses(message):
    print('getcourses_activate')
    user = Users.objects.get(id_tg=message.chat.id)
    id_moodle = user.id_moodle
    url = f"{MOODLE_URL}/webservice/rest/server.php?wstoken={MOODLE_TOKEN}&wsfunction=core_enrol_get_users_courses&userid={id_moodle}&moodlewsrestformat=json"
    response = requests.get(url)
    courses = json.loads(response.text)
    if (not courses):
        bot.send_message(message.chat.id, "вы не записаны ни на один курс")
    else:
        text = ''
        for course in courses:
            text += f"{course['fullname']} ({course['shortname']} {course['id']})\n"
        bot.send_message(message.chat.id, text)


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
        user, created = Users.objects.get_or_create(id_tg=message.chat.id, defaults={'id_moodle':id_moodle})
        if (not created):
            bot.send_message(message.chat.id, "вы уже записаны в базу бота")
            bot.send_message(message.chat.id, f"{user.id_tg} {user.id_moodle}")
        else:
            bot.send_message(message.chat.id, "вac записали в базу бота")
            bot.send_message(message.chat.id, f"{user.id_tg} {user.id_moodle}")

bot.polling(none_stop=True)