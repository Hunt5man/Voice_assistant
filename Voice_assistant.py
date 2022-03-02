import os
import re
import sys
import datetime
import speech_recognition as sr
import pyttsx3
import random
import webbrowser
import wikipedia
import pyowm
from pyowm.utils.config import get_default_config
from googletrans import Translator
from pytils import numeral
import pymorphy2
import warnings

warnings.filterwarnings("ignore")

opts = {
    'wiki': ('что такое', 'что значит', 'на википедии', 'нужна справка', 'нужна информация',
             'дай информацию', 'в википедии', 'википедия', 'википедию', 'информацию', 'информация', 'на'),
    'google_search': ('найди в гугле', 'посмотри в гугле', 'нагугли', 'нужна справка в гугле',
                      'нужна информация в гугле', 'дай информацию в гугле', 'загугли', 'гугл',
                      'гугли', 'в гугле', 'гугле'),
    'time': ('текущее время', 'сейчас времени', 'который час', 'сейчас натикало'),
    'site': ('сайт', 'на сайт', 'страничка', 'на страничку', 'страница', 'на страницу', 'на'),
    'process': ('Секундочку...', 'Уже смотрю...', 'Сейчас...'),
    'pretext': ('про', 'об', 'о об'),
    'translate': ('язык', 'на'),
    'request_yes': ('да, продолжай', 'да, продолжай рассказывать', 'продолжай', 'продолжай рассказывать',
                    'давай дальше', 'рассказывай', 'говори', 'давай до конца', 'продолжи',
                    'продолжи рассказывать', 'тогда продолжай рассказывать'),
    'request_no': ('открой сайт', 'я хочу сам', 'я сам', 'давай сайт', 'открывай сайт', 'пожалуй я сам',
                    'я сам изучу', 'я сам почитаю', 'я самостоятельный', 'покажи сайт', 'сайт'),
    'request_stop': ('хватит', 'ничего не нужно', 'нет, ничего не нужно', 'ничего не надо', 'ничего не делай'),
    'need_removed': ('скажи', 'покажи', 'расскажи', 'зайди', 'посмотри', 'глянь', 'заскочи',
                     'чекни', 'дай знать', 'проверь', 'выведи на экран', 'выведи на монитор',
                     'выведи', 'дай информацию по', 'дай инфу по', 'сколько', 'произнеси',
                     'еще раз', 'тогда', 'еще', 'перейди', 'открой', 'узнай', 'какая сейчас',
                     'какая', 'какой-нибудь', 'еще один', 'еще одно', 'нужно', 'найди информацию',
                     'пожалуйста', 'мне', 'найди информацию по', 'найди', 'информацию')
}

def speak(audio):
    print(audio)
    speak_engine.say(audio)
    speak_engine.runAndWait()
    speak_engine.stop()

def myCommand():
    try:
        command = r.recognize_google(audio, language="ru-RU").lower()
        #print('[!] Распознано:' + command)
    except sr.RequestError as e:
        speak('[!] Неизвестная ошибка, проверьте интернет!')
    except sr.UnknownValueError:
        command = myCommand()
        speak('[!] Я Вас плохо слышу, повторите пожалуйста!')
    return command

def start(command):
    if 'катрина' in command:
        hour = int(datetime.datetime.now().hour)
        if hour >= 6 and hour < 10:
            speak("Доброе утро! Я Вас слушаю")
        elif hour >= 10 and hour < 18:
            speak("Добрый день! Я Вас слушаю")
        elif hour >= 18 and hour < 22:
            speak("Добрый вечер! Я Вас слушаю")
        else:
            speak("Добрый ночи. Я Вас слушаю")
        with m as source:
            r.adjust_for_ambient_noise(source, duration=3)
        while True:
            with m as source:
                audio = r.listen(source, timeout=None, phrase_time_limit=5)
                command = r.recognize_google(audio, language="ru-RU").lower()
            assistant(command)
    else:
        pass

def assistant(command):
    if 'погода' in command or 'температура' in command:
        try:
            result_weather = re.search('в (.*)', command)
            if not result_weather:
                speak('Я не поняла где. Скажите еще раз')
            else:
                morph = pymorphy2.MorphAnalyzer()
                city_not_correct = result_weather.group(1)
                city = morph.parse(city_not_correct)[0].normal_form
                speak(random.choice(opts['process']))
                config_dict = get_default_config()
                config_dict['language'] = 'ru'
                owm = pyowm.OWM('a4db9e993b32d6d3aca85044d2595004', config_dict)
                mgr = owm.weather_manager()
                observation = mgr.weather_at_place(city)
                w = observation.weather
                temp = w.temperature('celsius')['temp']
                speak('В ' + city_not_correct.title() + ' сейчас температура: ' + str(temp) + ' градусов по Цельсию, ' + w.detailed_status + '.')
        except AttributeError:
            speak('Я не услышала название. Повторите пожалуйста')
        except pyowm.commons.exceptions.NotFoundError:
            speak('Я не поняла город. Скажите еще раз')

    elif 'сайт' in command or 'страницу' in command or 'страничку' in command:
        for e in opts['need_removed']:
            command = command.replace(e, '').strip()
        for e in opts['site']:
            command = command.replace(e, '').strip()
        try:
            result_site = re.search('(.*)', command)
            site = result_site.group(1)
            if not site:
                speak('Я не поняла название сайта. Скажите еще раз')
            else:
                url = 'https://www.' + site
                webbrowser.open(url)
                speak('Я открыла сайт, который вы просили')
        except pyowm.commons.exceptions.NotFoundError:
            speak('Я не нашла такой сайт. Повторите еще раз название')

    elif 'время' in command or 'времени' in command or 'который час' in command or 'который сейчас час' in command:
        for e in opts['time']:
            command = command.replace(e, '').strip()
        now = datetime.datetime.now()
        h = now.hour
        m = now.minute
        speak("Сейчас %s %s" % (
            numeral.get_plural(h, "час, часа, часов"),
            numeral.get_plural(m, "минута, минуты, минут"),
        )
        )

    elif 'шутку' in command or 'пошути' in command or 'рассмеши' in command or 'что-то смешное' in command:
        joke = ('Самоуничтожение начнется через 10...9...8...7...6....', 'Чем больше самоубийц, тем меньше самоубийц',
                 'Интересно, какой дадут срок, если в Майнкрафте пройтись голым возле храма?',
                 'Послеродовая депрессия - это когда ты родился и живешь.',
                 'Диалог: водка есть? Ты что не русский? Водка - это пить.', 'Пока комар пищит, он не кусает.')
        speak(random.choice(joke))

    elif 'гугл' in command or 'гугле' in command or 'загугли' in command:
        for e in opts['google_search']:
            command = command.replace(e, '').strip()
        for e in opts['need_removed']:
            command = command.replace(e, '').strip()
        for e in opts['pretext']:
            command = command.replace(e, '').strip()
        try:
            result_google_search = re.search('(.*)', command)
            morph = pymorphy2.MorphAnalyzer()
            request = result_google_search.group(1).split()
            if not request:
                speak('Я не услышала что Вы ищете. Скажите еще раз')
            else:
                i = 0
                for word in request:
                    request[i] = morph.parse(word)[0].normal_form
                    i += 1
                request_link = ' '.join(request)
                url = 'https://www.google.com/search?q=' + request_link
                webbrowser.open(url)
                speak('Вот результаты поиска по Вашему запросу')
        except pyowm.commons.exceptions.NotFoundError:
            speak('Я не поняла что Вы ищете. Скажите еще раз')

    elif 'википедии' in command or 'википедию' in command or 'википедия' in command:
        for e in opts['need_removed']:
            command = command.replace(e, '').strip()
        for e in opts['wiki']:
            command = command.replace(e, '').strip()
        for e in opts['pretext']:
            command = command.replace(e, '').strip()
        try:
            result_wiki = re.search('(.*)', command)
            request = result_wiki.group(1)
            wikipedia.set_lang("ru")
            result = wikipedia.summary(request, sentences=2)
            speak(result)
            speak('Мне продолжить рассказывать или открыть Вам сайт для самостоятельного изучения?')
            while True:
                try:
                    with sr.Microphone(device_index=1) as source:
                        audio_answer = r.listen(source, phrase_time_limit=5)
                        answer = r.recognize_google(audio_answer, language="ru-RU").lower()
                    if answer.startswith(opts['request_yes']):
                        speak('Хорошо, рассказываю статью...')
                        result = wikipedia.summary(request, sentences=10)
                        speak(result)
                        break
                    elif answer.startswith(opts['request_no']):
                        speak('Секундочку...')
                        page = wikipedia.page(result)
                        webbrowser.open(page.url)
                        speak('Я открыла Вам сайт')
                        break
                    elif answer.startswith(opts['request_stop']):
                        speak('Поняла. Молчу')
                        break
                    else:
                        speak('Я не поняла, что мне нужно сделать')
                except wikipedia.exceptions.WikipediaException:
                    speak('Извините, но поисковый запрос слишком большой')
                except pyowm.commons.exceptions.NotFoundError:
                    speak('Я Вас не поняла. Скажите еще раз')
        except wikipedia.exceptions.WikipediaException:
            speak('Я не поняла, что мне искать. Повторите запрос пожалуйста')
        except wikipedia.exceptions.DisambiguationError:
            speak('Слишком много вариаций запроса. Уточните пожалуйста')
        except wikipedia.exceptions.PageError:
            speak('Я не нашла такой страницы на википедии')

    elif 'видео' in command or 'трейлер' in command:
        for e in opts['pretext']:
            command = command.replace(e, '').strip()
        try:
            result_video = re.search('видео (.*)', command) or re.search('трейлер (.*)', command)
            morph = pymorphy2.MorphAnalyzer()
            video = result_video.group(1).split()
            i = 0
            for word in video:
                video[i] = morph.parse(word)[0].normal_form
                i += 1
            video_link = ' '.join(video)
            url = "https://www.youtube.com/results?search_query=" + video_link
            webbrowser.open(url)
            speak('Здесь видео, которое вы искали')
        except AttributeError:
            speak('Я не услышала название. Повторите пожалуйста')
        except pyowm.commons.exceptions.NotFoundError:
            speak('Я не поняла название видео. Скажите еще раз')

    elif 'музыку' in command:
        speak('Секундочку...')
        os.startfile('C:/Program Files (x86)/AIMP/AIMP.exe')

    elif 'блокнот' in command:
        speak('Открываю блокнот...')
        os.startfile('C:/Windows/System32/notepad.exe')
        speak('Готово')

    elif 'калькулятор' in command:
        speak('Запускаю калькулятор...')
        os.startfile('C:/Windows/System32/calc.exe')
        speak('Готово')

    elif 'запусти' in command or 'открой' in command:
        speak('Уже работаю над этим...')
        try:
            searching_exe = re.search('открой (.*)', command) or re.search('запусти (.*)', command)
            result_searching_exe = searching_exe.group(1)
            name_file = result_searching_exe + ".exe"
            if not result_searching_exe:
                speak('Я не поняла что мне открыть. Скажите еще раз')
            else:
                for root, dirs, files in os.walk(r'C:\Program Files (x86)'):
                    for name in files:
                        if name.endswith('.exe') and name.lower() == name_file:
                            os.startfile(os.path.join(root, name))
                            speak('Я открыла, что вы просили')
        except FileNotFoundError:
            speak('Мне не удалось найти указанный файл')

    elif 'переведи' in command:
        for e in opts['need_removed']:
            command = command.replace(e, '').strip()
        for e in opts['translate']:
            command = command.replace(e, '').strip()
        if 'английский' in command:
            try:
                searching_text = re.search('английский (.*)', command)
                text_to_translate = searching_text.group(1)
                print('Оригинал: ' + text_to_translate.capitalize())
                translator = Translator()
                result = translator.translate(text_to_translate, dest='en')
                speak_engine.setProperty('voice', voices[2].id)
                speak_engine.setProperty('rate', 145)
                print('Перевод: ', end='')
                speak(result.text.capitalize())
                speak_engine.setProperty('voice', voices[0].id)
                speak_engine.setProperty('rate', 235)
            except AttributeError:
                speak_engine.setProperty('voice', voices[0].id)
                speak_engine.setProperty('rate', 235)
                speak('Я не поняла что перевести. Повторите пожалуйста')

        elif 'немецкий' in command:
            try:
                searching_text = re.search('немецкий (.*)', command)
                text_to_translate = searching_text.group(1)
                print('Оригинал: ' + text_to_translate.capitalize())
                translator = Translator()
                result = translator.translate(text_to_translate, dest='de')
                speak_engine.setProperty('voice', voices[4].id)
                speak_engine.setProperty('rate', 170)
                print('Перевод: ', end='')
                speak(result.text.capitalize())
                speak_engine.setProperty('voice', voices[0].id)
                speak_engine.setProperty('rate', 235)
            except AttributeError:
                speak_engine.setProperty('voice', voices[0].id)
                speak_engine.setProperty('rate', 250)
                speak('Я не поняла что перевести. Повторите пожалуйста')

        elif 'итальянский' in command:
            try:
                searching_text = re.search('итальянский (.*)', command)
                text_to_translate = searching_text.group(1)
                print('Оригинал: ' + text_to_translate.capitalize())
                translator = Translator()
                result = translator.translate(text_to_translate, dest='it')
                speak_engine.setProperty('voice', voices[3].id)
                speak_engine.setProperty('rate', 170)
                print('Перевод: ', end='')
                speak(result.text.capitalize())
                speak_engine.setProperty('voice', voices[0].id)
                speak_engine.setProperty('rate', 235)
            except AttributeError:
                speak_engine.setProperty('voice', voices[0].id)
                speak_engine.setProperty('rate', 235)
                speak('Я не поняла что перевести. Повторите пожалуйста')

        elif 'русский' in command:
            try:
                searching_text = re.search('русский (.*)', command)
                text_to_translate = searching_text.group(1)
                print('Оригинал: ' + text_to_translate.capitalize())
                translator = Translator()
                result = translator.translate(text_to_translate, dest='ru')
                print('Перевод: ', end='')
                speak(result.text.title())
            except AttributeError:
                speak('Я не поняла что перевести. Повторите пожалуйста')
        else:
            speak('Я не поняла на какой язык и что перевести')

    elif 'спасибо' in command or 'благодарю' in command or 'молодец' in command:
        thanks = ('Пожалуйста', 'Без проблем', 'Обращайтесь еще')
        speak(random.choice(thanks))

    elif 'отключись' in command or 'выключись' in command:
        speak_bye = ('До свидания', 'Всего доброго', 'Удачи Вам')
        hour = int(datetime.datetime.now().hour)
        if hour >= 6 and hour < 10:
            speak(random.choice(speak_bye) + " и хорошего Вам утра!")
        elif hour >= 10 and hour < 18:
            speak(random.choice(speak_bye) + " и хорошего Вам дня!")
        elif hour >= 18 and hour < 22:
            speak(random.choice(speak_bye) + " и хорошего Вам вечера!")
        else:
            speak(random.choice(speak_bye) + " и доброй ночи.")
        sys.exit()

r = sr.Recognizer()
m = sr.Microphone(device_index=1)
r.dynamic_energy_threshold = False
r.energy_threshold = 1000
r.pause_threshold = 0.5
speak_engine = pyttsx3.init()
voices = speak_engine.getProperty('voices')
speak_engine.setProperty('rate', 233)

with m as source:
    r.adjust_for_ambient_noise(source, duration=3)

while True:
    with m as source:
        audio = r.listen(source, timeout=None, phrase_time_limit=5)
    start(myCommand())