import requests
import os
import time
import sys
from dotenv import load_dotenv


def createConversationJson(history):
    element = {
        "model": "gpt-3.5-turbo",
        "messages": []
        }
    if len(history) > 0:
        for item in history:
            element['messages'].append(item[0])

    return element

def getChatGPTAnswer(api_key,history):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}" 
    }
    data = createConversationJson(history)
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    return response.json()['choices'][0]['message']['content']

def sendTelegramMessage(api_key, chat_id, message):
    requests.post(f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={message}')

def getLastTelegramMessage(api_key):
    url = f'https://api.telegram.org/bot{api_key}/getUpdates'
    result = requests.post(url).json()
    length = len(result['result'])
    return result['result'][length-1]['message']['text']


def handleCommand(telegram_bot_key, telegram_chat_id, command):
    if command == '/zynisch' or command == '#ironisch': return ' sei dabei zynisch und ironisch'
    if command == '/pesimistisch': return ' sei dabei extrem pesimistisch'
    if command == '/fröhlich': return ' sei dabei extrem fröhlich'
    if command == '/verliebt': return ' tu so, als wärst du total in mich verliebt'
    if command == '/wütend': return ' sei dabei extrem wütend'
    if command == '/': sendTelegramMessage(telegram_bot_key, telegram_chat_id, 'Es gibt folgendes: /zynisch, /pesimistisch, /fröhlich, /verliebt, /wütend')
    return ''


def main():
    load_dotenv()
    telegram_bot_key = os.getenv('TELEGRAM_BOT_KEY')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    lastMessage = ''
    history = []
    mood = ''

    maxHistoryLength = 25
    if(len(history) > maxHistoryLength):
        history = history[len(history)-maxHistoryLength:]

    while True:
        try:
            message = getLastTelegramMessage(telegram_bot_key)
            if message[0] == '/' and message != lastMessage:
                mood = handleCommand(telegram_bot_key, telegram_chat_id, message)
                print(mood)
                lastMessage = message

            else:
                message += mood
                if lastMessage != message and message[0] != '/':
                    if message == 'clear':
                        history = []
                    else:
                        print(f"Question: {message}")
                        history.append([{"role": "user", "content": message}])
                        answer = getChatGPTAnswer(openai_api_key, history)
                        #answerToDisplay = answer.replace('\n', '%0A')
                        print(f"Answer: {answer}\n")
                        history.append([{"role": "system", "content": answer}])
                        sendTelegramMessage(telegram_bot_key, telegram_chat_id, answer)
                        lastMessage = message

        except:
            e = sys.exc_info()[0]
            answer = 'Oh fuck...'
            print(answer)
            print(e)

        time.sleep(2)

if __name__ == "__main__":
    main()