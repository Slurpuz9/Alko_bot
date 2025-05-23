# Импорт необходимых библиотек
import telebot
from telebot import types
import requests
import random
import re

# Инициализация бота с использованием токена
bot = telebot.TeleBot('')

# Список тостов для случайного выбора
with open('Toasts.txt', 'r', encoding='utf-8') as f:
    TOASTS = [i.rstrip() for i in f]

# Открываем картинки для сообщений и создаем список для случайного выбора
photo1 = open('photos\photo1.jpg', 'rb')
photo2 = open('photos\photo2.jpg', 'rb')
photo3 = open('photos\photo3.jpg', 'rb')

photo_ban = open('photos\photo_ban.jpg', 'rb')

PHOTOS = [photo1, photo2, photo3]

# Загружаем список русских имён (мужских и женских почти во всех формах)
with open('names\Female_names_rus.txt', 'r', encoding='utf-8') as f:
    F_NAMES = [i.rstrip().lower() for i in f]
with open('names\Male_names_rus.txt', 'r', encoding='utf-8') as f:
    M_NAMES = [i.rstrip().lower() for i in f]
# С помощью множеств делаем список единым (формат множеств пригодится в дальнейшем)
F_NAMES = set(F_NAMES)
M_NAMES = set(M_NAMES)

NAMES = F_NAMES | M_NAMES

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Приветственное сообщение с проверкой возраста.
    Создает инлайн-клавиатуру с кнопками "Да"/"Нет".
    """
    # Создание разметки клавиатуры
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Да', callback_data='yes'))
    markup.add(types.InlineKeyboardButton('Нет', callback_data='no'))

    # Отправка вопроса о возрасте
    bot.reply_to(message, 'Вам больше 18?', reply_markup=markup)


# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda callback: True)
def handle_age_check(callback):
    """
    Обрабатывает ответ пользователя на проверку возраста.
    """
    if callback.data == 'no':
        # Если пользователь младше 18 лет
        bot.send_message(callback.message.chat.id, 'Еще рановато!')
        bot.send_photo(callback.message.chat.id, photo=photo_ban)
    elif callback.data == 'yes':
        # Запрос дополнительной информации
        bot.send_message(
            callback.message.chat.id,
            'Ответьте на вопросы: Как вас зовут? Сколько вы выпили? Кто с вами пьет? Где вы находитесь?'
        )
        # Регистрация следующего шага обработки
        bot.register_next_step_handler(callback.message, check_alcohol_status)


def check_alcohol_status(message):
    """
    Проверяет сообщение пользователя на наличие опечаток и длину текста.
    Определяет состояние пользователя на основе ответа.
    """
    user_text = message.text.strip().lower()

    # Проверка орфографии через Яндекс.Спеллер
    spell_check_url = f'https://speller.yandex.net/services/spellservice.json/checkText?text={user_text}'
    response = requests.get(spell_check_url)
    spell_errors = response.json()
    WORDS = re.split(r'[ ,.?\!]+', user_text)
    WORDS = set(WORDS)
    if WORDS & NAMES | {'test'} == {'test'}:
        bot.send_message(message.chat.id, 'Вы даже не представились! Давайте еще раз!')
        bot.register_next_step_handler(message, check_alcohol_status)
    else:
        Person_nameing = WORDS & NAMES
        Person_name = random.choice(list(Person_nameing)).title()
        # Проверка длины сообщения
        if len(user_text) < 25:
            if len(spell_errors) > 0:
                # Короткий текст с ошибками
                bot.send_message(message.chat.id, f'Вызовите скорую!{Person_name} не справляется с односложными предложениями!')
                bot.send_photo(message.chat.id, photo=photo_ban)
            else:
                # Короткий текст без ошибок
                bot.send_message(
                    message.chat.id,
                    f'Ну да, такой короткий рассказ я даже мертвым напишу! Еще раз, {Person_name}!'
                )
                # Повторная регистрация обработчика
                bot.register_next_step_handler(message, check_alcohol_status)
        else:
            if len(spell_errors) > 0:
                # Длинный текст с ошибками
                bot.send_message(message.chat.id, f'{Person_name}, Похоже вам уже хватит )')
                bot.send_photo(message.chat.id, photo=photo_ban)
            else:
                # Успешная проверка - случайный тост
                toast_index = random.randint(0, len(TOASTS) - 1)
                photo_index = random.randint(0, len(PHOTOS) - 1)
                bot.send_message(message.chat.id, f'Вперёд! {Person_name}. {TOASTS[toast_index]}!')
                bot.send_photo(message.chat.id, photo=PHOTOS[photo_index])
                PHOTOS[photo_index].seek(0)



# Запуск бота
bot.polling(none_stop=True)