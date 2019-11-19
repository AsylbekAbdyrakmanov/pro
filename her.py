import platform
import os
import youtube_dl
import telebot
from sys import argv
import re
from datetime import datetime

bot = telebot.TeleBot('1006252900:AAFh8XaeGgjVfQl_AW_RgXx5U0Q64pWk6N0')

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
keyboard.row('mp3','mp4')

format_ = None
youtube_url = None

RESERVED_CHARS = ['|', '<', '>', ':', '"', '/', '\\', '?', '*', '^', '&', '+', '-', '%', '=', '!', ',', '(', ')', '$']

DOWNLOAD_OPTIONS_MP3 = {
            'format': 'bestaudio/best',
            'outtmpl': '%(id)s.%(ext)s',
            'nocheckcertificate' : True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

DOWNLOAD_OPTIONS_MP4 = {
            'format': 'best',
            'outtmpl': '%(id)s.%(ext)s',
            'nocheckcertificate' : True,
        }

@bot.message_handler(commands=['start'])
def start_message(message):
    description = 'Здарова! Я mp3 & mp4 конвертер  \nСкидывай мне ссылку видео из Ютуба (пока что с Ютуба) и я отправлю тебе файл в формате mp3 или mp4, с уважением бот Асылбека'
    bot.send_message(message.chat.id, description)

@bot.message_handler(regexp = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$')
def get_info(message):
    global format_
    global youtube_url
    youtube_url = message
    bot.send_sticker(message.chat.id, 'CAADBQADgAMAAukKyAOXWG874z7K-BYE')
    format_choose = bot.send_message(message.chat.id, 'Выберите формат', reply_markup=keyboard)
    bot.register_next_step_handler(format_choose, mp3_or_mp4)

def mp3_or_mp4(message):
    if message.text == 'mp3':
        get_mp3(youtube_url)
    elif message.text == 'mp4':
        get_mp4(youtube_url)
    else:
        msg = bot.send_message(message.chat.id, 'Вы должны нажать на mp3 или mp4')
        bot.register_next_step_handler(msg, mp3_or_mp4)

def get_mp3(message):
    with youtube_dl.YoutubeDL(DOWNLOAD_OPTIONS_MP3) as dl:
        result = dl.extract_info(youtube_url.text, download=False)
        id_ = result['id']
        title = result['title']
        title = check_title_for_reserved_chars(title)
        bot.send_sticker(message.chat.id, 'CAADAgADQgADIkwPDLRtlz5GAiUkFgQ')
        dl.download([youtube_url.text])
        rename_file_mp3(id_, title)
        bot.send_audio(message.chat.id, audio=open(title + '.mp3', 'rb'))
        bot.send_sticker(message.chat.id, 'CAADBQADwAMAAukKyAOjljyyS-dv2BYE')
        save_info_mp3(message)
        delete_file_mp3(message, id_, title)

def get_mp4(message):
    with youtube_dl.YoutubeDL(DOWNLOAD_OPTIONS_MP4) as dl:
        result = dl.extract_info(youtube_url.text, download=False)
        id_ = result['id']
        title = result['title']
        title = check_title_for_reserved_chars(title)
        dl.download([youtube_url.text])
        rename_file_mp4(id_, title)
        bot.send_sticker(message.chat.id, 'CAADAgADQgADIkwPDLRtlz5GAiUkFgQ')
        bot.send_video(message.chat.id, data=open(title + '.mp4', 'rb'))
        bot.send_sticker(message.chat.id, 'CAADBQADwAMAAukKyAOjljyyS-dv2BYE')
        save_info_mp4(message)
        delete_file_mp4(message, id_, title)

@bot.message_handler(content_types=['text', 'sticker', 'audio', 'document', 'video', 'voice', 'location', 'video_note', 'contact'])
def send_message(message):
    bot.send_sticker(message.chat.id, 'CAADBQADgQMAAukKyANDdDlhDY7IuRYE')

def save_info_mp3(message):
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    data_file = open('data_mp3.txt', 'a+')
    data_file.write(f'{date}\t{message.from_user.first_name} {message.from_user.last_name} {message.from_user.username}\t{message.text}\n')
    data_file.close()

def save_info_mp4(message):
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    data_file = open('data_mp4.txt', 'a+')
    data_file.write(f'{date}\t{message.from_user.first_name} {message.from_user.last_name}\t{message.text}\n')
    data_file.close()


def delete_file_mp3(message, id_, title):
    if platform.system() == 'Linux':
        if os.path.exists(f'{title}.mp3'):
            os.system(f'rm -rf {title}.mp3')
        if os.path.exists(f'{id_}.mp3'):
            os.system(f'rm -rf {id_}.mp3')  
    elif platform.system() == 'Windows':
        if os.path.exists(f'{title}.mp3'):
            os.system(f'del {title}.mp3')
        if os.path.exists(f'{id_}.mp3'):
            os.system(f'del {id_}.mp3')

def delete_file_mp4(message, id_, title):
    if platform.system() == 'Linux':
        if os.path.exists(f'{title}.mp4'):
            os.system(f'rm -rf {title}.mp4')
        elif os.path.exists(f'{id_}.mp4'):
            os.system(f'rm -rf {id_}.mp4')  
    elif platform.system() == 'Windows':
        if os.path.exists(f'{title}.mp4'):
            os.system(f'del {title}.mp4')
        elif os.path.exists(f'{id_}.mp4'):
            os.system(f'del {id_}.mp4')

def rename_file_mp3(prev, current):
    if platform.system() == 'Linux':
        os.system(f'mv {prev}.mp3 {current}.mp3')
    elif platform.system() == 'Windows':
        os.system(f'rename {prev}.mp3 {current}.mp3')

def rename_file_mp4(prev, current):
    if platform.system() == 'Linux':
        os.system(f'mv {prev}.mp4 {current}.mp4')
    elif platform.system() == 'Windows':
        os.system(f'rename {prev}.mp4 {current}.mp4')

def check_title_for_reserved_chars(title):
  for char in RESERVED_CHARS:
    while char in title:
      title = title.replace(char, '')
  while ' ' in title:
    title = title.replace(' ', '_')
  return title

bot.polling()
