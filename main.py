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


def main():
    load_dotenv()

    telegram_bot_key = os.getenv('TELEGRAM_BOT_KEY')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    print(openai_api_key)

    oldMessage = ''
    history = []

    while True:
        #try:
        message = getLastTelegramMessage(telegram_bot_key)
        if oldMessage != message:
            if message == 'clear':
                history = []
            else:
                print(f"Question: {message}")
                history.append([{"role": "user", "content": message}])
                answer = getChatGPTAnswer(openai_api_key, history)
                print(f"Answer: {answer}\n")
                history.append([{"role": "system", "content": answer}])
                sendTelegramMessage(telegram_bot_key, telegram_chat_id, answer)
                oldMessage = message

        #except:
        #    e = sys.exc_info()[0]
        #    answer = 'Oh fuck...'
        #    print(answer)
        #    print(e)

        time.sleep(1)

if __name__ == "__main__":
    main()