import json
from collections import Counter
from datetime import datetime
with open('result.json','r',encoding='utf-8') as json_file:
    data = json.load(json_file)
valid_symbols = " ?!@#$%^&*()><_-+=абвгдаеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz0123456789.,:;/n"
your_id = 0

def checkSymbs( text ):
    global badSymbols
    badSymbols = ''
    for c in text:
        if c not in valid_symbols:
            badSymbols += c
            return False

    return True


myMessages = []
lastDate = None

for chat in data['chats']['list']:
    if ('name' in chat and 'messages' in chat and len( chat['messages'] ) > 10):
        # print(chat['name'] + " " + str(len(chat['messages'])))
        for msg in chat['messages']:
            if ('type' in msg and msg['type'] == 'message'):
                if ('text' in msg and len( msg['text'] ) >= 2):
                    date = datetime.strptime( msg['date'], "%Y-%m-%dT%H:%M:%S" ).timestamp()
                    if lastDate != None and (date - lastDate > 600):
                        myMessages.append( "===" )
                    lastDate = date
                    prefix = '> '
                    if ('from_id' in msg and msg['from_id'] != your_id):
                        prefix = '< '
                    text = str( msg['text'] )
                    #date
                    if not text.startswith( '[' ) and not """://""" in text:
                        t = str( msg['text'] ).lower()
                        t = t.replace( '\n', ' ' ).replace( '\r', ' ' ).replace( '\t', ' ' ).replace( '\"',
                                                                                                      '' ).replace(
                            '\'', '' )
                        t = t.replace( '  ', ' ' )
                        if checkSymbs( t ):
                            myMessages.append( prefix + t )

print( len( myMessages ) )
print(len(myMessages))
print(myMessages)
with open('myMessagesTelegram.txt', mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(str(line) for line in myMessages))
