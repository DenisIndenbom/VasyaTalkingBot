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
@bot.message_handler(commands=['start'])
def Start(message: Message):
    user: User = message.from_user
    bot.send_message(message.chat.id,
                     'Привет!\U0001F91A	Я чат бот\U0001F916 и я люблю поболтать\U0001F4C3.')
    writeLog(f"{user.first_name}: {message.text}")
@bot.message_handler(content_types=['text'])
def talk(message: Message):
    answer = ""
    global model
    user: User = message.from_user
    text = message.text
    try:
        answer = model.generate_text( f'< {text}\n> ', True, 0.35)
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

bot.polling(none_stop=True)
