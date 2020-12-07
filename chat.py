import telebot
from telebot.types import Message, User
import dialogModel as rnn
import datetime
import keepAwake
keepAwake.enable()


model = rnn.Model( 'idx2char.npy', 'ckpt_35' )
token = "secret"
def writeMessage(user,question,answer):
    writeLog(f'{user}: {question}\nВася: {answer}')


def writeLog(text):
    with open("log.txt", "at", encoding="utf-8-sig") as bd:
        bd.write(text + '\n')

    print(text)
# Обходим блокировку с помощью прокси
telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}
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
                                     '\n/description - описание'
                                     '\n/ver - версия бота и размер его датасета'
                                     '\n/news - новости последнего обновления'
                                     '\n/creator - создатель'
                                     '\n/github - исходники')
@bot.message_handler(commands=['ver'])
def ver(message: Message):
    bot.send_message( message.chat.id,"Версия бота 1.6;\nРазмер датасета 330573 сообщений;\nКол-во параметров нейронной сети 6,520,290;")
@bot.message_handler(commands=['news'])
def ver(message: Message):
    bot.send_message( message.chat.id,"Обновление 1.6!\n"
                                      "\nЧто нового:"
                                      "\n - датасет увеличен в 6 раз => Вася отвечает корректнее \n   и осмысленнее.(Датасет - это начём учится нейроная сеть)"
                                      "\n"
                                      "\nВывод:"
                                      "\n В этом обновление Вася отвечает корректнее и осмысленнее."
                                      "\n То-есть лучше составляет предложения по контексту вопроса.")
@bot.message_handler(commands=['description'])
def send_description(message: Message):
    bot.send_message(message.chat.id,'Вася - говорящий бот.'
                                     '\n'
                                     '\nОн может поболтать с вами о чём угодно, но может отвечать некорректно.'
                                     '\n'
                                     '\nБот использует RNN(рекуррентная нейронная сеть) для генерации текста.'
                                     '\n'
                                     '\nНа данный момент бот обучается говорить лучше.'
                                     'Может через некоторое время он станет намного лучше чем сейчас.')

@bot.message_handler(commands=['start'])
def start(message: Message):
    user: User = message.from_user
    bot.send_message(message.chat.id,
                     'Привет!\U0001F91A. Я говорящий чат бот \U0001F916. Я использую нейронные сети для генерации текста'
                     '\nПомощь:/help'
                     '\nСсылка на gitHub: https://github.com/DenisIndenbom/VasyaTalkingBot')
    writeLog(f"{user.first_name}: {message.text}")

@bot.message_handler(content_types=['text'])
def talk(message: Message):
    answer = ""
    global model
    user: User = message.from_user
    text = message.text.replace('-','')
    if "main" in text:
        bot.send_message( message.chat.id, 'Не понял' )
    else:
        try:
            answer = model.generate_text( f'< {text}\n> ', True, 0.15)
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
bot.polling(none_stop=True,timeout=100)
