import telebot 
import requests
import json
from settings3 import bot_token, moodle_token, moodle_url

print('mainstart')

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['getcourses'])
def getcourses(message):
    print('getcourses_activate')
    url = f"{moodle_url}/webservice/rest/server.php?wstoken={moodle_token}&wsfunction=core_course_get_courses&moodlewsrestformat=json"
    response = requests.get(url)
    courses = json.loads(response.text)
    text = ''
    for course in courses:
        text += f"{course['fullname']} ({course['shortname']})\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['start'])
def start(message):
    print('start_activate')
    username = message.from_user.username
    url = f"{moodle_url}/webservice/rest/server.php?wstoken={moodle_token}&wsfunction=get_user_by_field_tg&username_tg={username}&moodlewsrestformat=json"
    response = requests.get(url)
    print('1')
    id_moodle = json.loads(response.text)
    print('2')
    if (id_moodle == None):
        bot.send_message(message.chat.id, 'вы не записали свой username')
        print('in')
    else:
        id_moodle = json.loads(response.text)
        bot.send_message(message.chat.id, id_moodle)
        print('in2')

if __name__ == '__main__':
    bot.polling(none_stop=True)