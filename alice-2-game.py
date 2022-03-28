import os

from flask import Flask, request
import logging
import json
from googletrans import Translator

translator = Translator()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}



@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON, который отправила нам Алиса в запросе POST
def main():
    logging.info('Request: %r', request.json)

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи библиотеки json преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog. Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)



def handle_dialog(req, res):
    user_id = req['session']['user_id']
    init = 'Переведи слово'
    if req['session']['new']:
        res['response']['text'] = f'Привет! Что тебе перевести?'
        return

    # Сюда дойдем только, если пользователь не новый, и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст, что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо', то мы считаем, что пользователь не согласился.
    # Подумайте, все ли в этом фрагменте написано "красиво"?\
    phrase = req['request']['original_utterance'].lower()
    if len(phrase) > len(init):
        if phrase[:len(init)] == 'переведи слово' or phrase[:len(init)] == 'переведите слово':
            word = phrase[len(init):]
            translated_word = translator.translate(word, src='ru', dest='en')
            res['response']['text'] = f'{translated_word.text}'
        else:
            res['response']['text'] = 'Не поняла команы'
    else:
        res['response']['text'] = 'Не поняла команы'
    return


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
