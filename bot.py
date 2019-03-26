import telebot
import json
from random import choice
import requests
import os 
import tempfile
import magic
import mimetypes
import subprocess
from os import environ
from pprint import pprint

bot_text = '''
Howdy, how are you doing?
Source code on https://glitch.com/~{}
'''.format(environ['PROJECT_NAME'])


bot = telebot.TeleBot(environ['TELEGRAM_TOKEN'])
pprint(bot.get_me().__dict__)


def list(msgs):
    for m in msgs: 
        print(m)

        

bot.set_update_listener(list)

print("Iniciado el listener")


def fix_extension(file_path):
    type = magic.from_file(file_path, mime=True)#.decode("utf-8")
    extension = str(mimetypes.guess_extension(type, strict=False))
    if extension is not None:
        # I hate to have to use this s***, f*** jpe
        if '.jpe' in extension:
            extension = extension.replace('jpe', 'jpg')
        os.rename(file_path, file_path + extension)
        return file_path + extension
    else:
        return file_path



def download(url, params=None, headers=None):
    try:
        jstr = requests.get(url, params=params, headers=headers, stream=True)
        ext = os.path.splitext(url)[1].split('?')[0]
        f = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        for chunk in jstr.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    except IOError as e:
        return None
    f.seek(0)
    if not ext:
        f.name = fix_extension(f.name)
    return open(f.name, 'rb')



def mp3_to_ogg(original):
    converted = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
    conv = subprocess.Popen(
        ['ffmpeg', '-i', original.name, '-ac', '1', '-c:a', 'libopus', '-b:a', '16k', '-y', converted.name],
        #['ffmpeg', '-i', original.name, '-acodec', 'pcm_u8', '-ar', '22050', converted.name],
        stdout=subprocess.PIPE)
    while True:
        data = conv.stdout.read(1024 * 100)
        if not data:
            break
        converted.write(data)
    #os.popen('cp {} audio.ogg'.format(converted.name))
    #return converted.name
    return open(converted.name, 'rb')

@bot.message_handler(commands=['tts'], func=lambda m: m.text and len(m.text.split()) > 1)
def ttsfunction(m):
    cid = m.chat.id
    #persona = ' '.join(m.text.split()[3:])
   # edu_el_mejor = any([True for x in persona.lower().split() if x in vips1 or any([True for y in vips1 if x.startswith(y)])])
  
    #submittedText = message.replace("/tts ","",1)
    nombre = m.from_user.first_name
    #respuesta =  "{} dijo {}".format(nombre, m.text.split(None, 1)[1])
    respuesta = m.text.split(None, 1)[1]
        # bot.send_message(cid, choice(insultos).format(persona))
    url = 'http://translate.google.com/translate_tts'
    params = {
        'tl': 'es',
        'q': respuesta,
        'ie': 'UTF-8',
        'total': len(respuesta),
        'idx': 0,
        'client': 'tw-ob',
    }
    headers = {
        "Referer": 'http://translate.google.com/',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.8 Safari/537.36"
    }
    jstr = requests.get(
        url,
        params=params,
        headers=headers
    )
    if jstr.status_code != 200:
        return bot.send_message(cid, respuesta)
    result_url = jstr.url
    voice = mp3_to_ogg(download(result_url, params=params, headers=headers))
    if voice:
        bot.send_voice(cid, voice)
    else:
        bot.send_message(cid, respuesta)



bot.set_webhook("https://{}.glitch.me/{}".format(environ['PROJECT_NAME'], environ['TELEGRAM_TOKEN']))