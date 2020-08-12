import telebot
from telebot.types import Message, User
import dialogModel as rnn
import datetime
#fitdate = datetime.datetime.now().hour + 1
model = rnn.Model( 'idx2char.npy', 'ckpt_30' )
token = "secret"
def writeMessage(user,question,answer):
    writeLog(f'{user}: {question}\nВася: {answer}')


def writeLog(text):
    with open("log.txt", "at", encoding="utf-8-sig") as bd:
        bd.write(text + '\n')

    print(text)
# Обходим блокировку с помощью прокси
telebot.apihelper.proxy = {'https': 'proxy'}
# подключаемся к телеграму
bot = telebot.TeleBot(token=token)

@bot.message_handler(commands=['github'])
def send_github(message: Message):
    bot.send_message(message.chat.id,'Ссылка на GitHub: https://github.com/DenisIndenbom/VasyaTalkingBot')
@bot.message_handler(commands=['creator'])
def send_creator(message: Message):
    bot.send_message(message.chat.id,'Меня создал Денис Инденбом.Все исходники на GitHub /github')

@bot.message_handler(commands=['help'])
def send_help(message: Message):
    bot.send_message(message.chat.id,'Я говорящий чат бот \U0001F916.'
                                     '\nЯ буду отвечать тебе на сообщение (просто напиши мне сообщение).'
                                     '\nВнимание бот может отвечать не совсем коректно!'
                                     '\nКоманды:'
                                     '\n/description'
                                     '\n/creator'
                                     '\n/github')

@bot.message_handler(commands=['description'])
def send_description(message: Message):
    bot.send_message(message.chat.id,'Вася - говорящий бот.'
                                     '\nОн сможет поболтать с вами о чём угодно, но может отвечать некорректно.'
                                     '\nНа данный момент бот обучается говорить лучше.'
                                     '\nМожет через некоторое время он станет намного лучше чем сейчас.')

@bot.message_handler(commands=['start'])
def start(message: Message):
    user: User = message.from_user
    bot.send_message(message.chat.id,
                     'Привет!\U0001F91A. Я чат бот \U0001F916 и я могу с тобой поболтать.'
                     '\nПомощь:/help'
                     '\nСсылка на gitHub: https://github.com/DenisIndenbom/VasyaTalkingBot')
    writeLog(f"{user.first_name}: {message.text}")

@bot.message_handler(content_types=['text'])
def talk(message: Message):
    answer = ""
    global model
    user: User = message.from_user
    text = message.text
    try:
        answer = model.generate_text( f'< {text}\n> ', True, 0.2)
        answer = answer.rstrip( '\n\r' )
        writeMessage( user.first_name, text, answer )
    except:
        try:
            bot.send_message( message.chat.id, 'В вашем сообщении не понятные для меня символы!' )
        except:
                print( "error:message didn't send" )

    try:
        bot.send_message( message.chat.id,answer)
    except:
        try:
            bot.send_message( message.chat.id, answer )
        except:
            print("error:message didn't send")
            while True:
                try:
                    bot.send_message( message.chat.id, answer )
                    break
                except:
                    pass
bot.polling(none_stop=True)
