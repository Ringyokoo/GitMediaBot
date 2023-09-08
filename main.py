import telebot
import subprocess
from telebot import types
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
bot = telebot.TeleBot('6585791083:AAE0NitcttD1YiClOLc_aM1GdSfzcARMAY0')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    photo = types.KeyboardButton('Добавить текст на фото')
    audio = types.KeyboardButton('Преобразовать текст в аудио')
    markup.add(photo, audio)
    bot.send_message(message.chat.id, f"Привет, {user}!", reply_markup=markup)

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
    Список доступных команд:
    /help - Показать список команд
    /stop - Остановить бот
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    photo = types.KeyboardButton('Добавить текст на фото')
    audio = types.KeyboardButton('Преобразовать текст в аудио')
    markup.add(photo, audio)
    bot.send_message(message.chat.id, help_text, reply_markup=markup)



# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    bot.send_message(message.chat.id, "Бот остановлен")
    bot.stop_polling()


@bot.message_handler(func=lambda message: message.text == 'Преобразовать текст в аудио')
def get_text(message):
    mess = 'Напишите текст, который надо преобразовать в аудио'
    bot.send_message(message.chat.id, mess)
    bot.register_next_step_handler(message, lambda message: handle_text_to_audio(message))
def handle_text_to_audio(message):
    chat_id = message.chat.id

    if message.text:
        text_to_speak = message.text

        # Команда 'gtts-cli' для создания аудио-файла (внешний сервис для синтеза речи Google Text-to-Speech)
        audio_file = 'output.mp3'
        subprocess.call(['gtts-cli', text_to_speak, '--output', audio_file])

        # Отправьте аудио-файл пользователю
        with open(audio_file, 'rb') as audio:
            bot.send_audio(chat_id, audio)
    else:
        bot.send_message(chat_id, "Вы отправили не текст. Пожалуйста, отправьте текст.")
        bot.register_next_step_handler(message, lambda message: handle_text_to_audio(message))


@bot.message_handler(func=lambda message: message.text == 'Добавить текст на фото')
def get_photo(message):
    mess = 'Прикрепите, пожалуйста, фото'
    bot.send_message(message.chat.id, mess)
    bot.register_next_step_handler(message, lambda message: handle_photo(message))
def handle_photo(message):
    chat_id = message.chat.id

    # Получите фотографию из сообщения
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    image = Image.open(BytesIO(file))

    bot.send_message(chat_id, "Теперь отправьте текст, который нужно добавить на фотографию.")

    bot.register_next_step_handler(message, lambda message: handle_text(message, image))

def handle_text(message, image):
    chat_id = message.chat.id
    if message.text:
        text_to_add = message.text

        # Добавьте текст на фотографию
        image_with_text = add_text_to_image(image, text_to_add)

        # Отправьте фотографию с текстом пользователю
        with BytesIO() as output:
            image_with_text.save(output, format="JPEG")
            output.seek(0)
            bot.send_photo(chat_id, photo=output)
    else:
        bot.send_message(chat_id, "Вы отправили не текст. Пожалуйста, отправьте текст.")
        bot.register_next_step_handler(message, lambda message: handle_text(message, image))

# Функция для добавления текста на фотографию
def add_text_to_image(image, text):
    draw = ImageDraw.Draw(image)
    fontsize = 80
    font = ImageFont.truetype("Gagalin.ttf", fontsize)
    caption = text
    text_bbox = draw.textbbox((0, 0), caption, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    image_width, image_height = image.size
    x = (image_width - text_width) / 2
    y = image_height - text_height - 50 # Положение текста снизу
    draw.text((x, y), caption, (0, 0, 0), font=font)
    return image

# Обработчик всех остальных сообщений, начинающихся с /
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def handle_other_commands(message):
    bot.send_message(message.chat.id, "Неизвестная команда. Используйте /help для просмотра списка команд.")

bot.polling(none_stop=True)