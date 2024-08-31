import telebot
from telebot.types import Message
import time

# Создаем бота с вашим API токеном
bot = telebot.TeleBot("7273841264:AAHYFTHox-gKmCcQfBtwR_jq47MjGETkhdY")

# Словари для хранения разрешений
admins = {
    'warn': [@WaB3pMa, @Doshik_1_8_5],  # Список ID пользователей, которые могут использовать команду /warn
    'mute': [@WaB3pMa, @Doshik_1_8_5],  # Список ID пользователей, которые могут использовать команду /mute
    'ban': [123456789],   # Список ID пользователей, которые могут использовать команду /ban
    'unmute': [@WaB3pMa, @Doshik_1_8_5] # Список ID пользователей, которые могут использовать команду /unmute
}

# Словарь для хранения предупреждений
warnings = {}

# Словарь для хранения времени окончания мута
mute_until = {}

# Проверка, является ли сообщение от бота
def is_bot_message(message):
    return message.from_user.id == bot.get_me().id

# Проверка, имеет ли пользователь доступ к команде
def has_permission(user_id, command):
    return user_id in admins.get(command, [])

# Функция предупреждения пользователя
@bot.message_handler(commands=['warn'])
def warn_user(message: Message):
    if is_bot_message(message):
        bot.reply_to(message, "Нельзя влиять на бота.")
        return

    user_id = message.from_user.id
    if not has_permission(user_id, 'warn'):
        bot.reply_to(message, "У вас нет прав для использования этой команды.")
        return

    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id

        # Увеличиваем количество предупреждений
        warnings[target_user_id] = warnings.get(target_user_id, 0) + 1

        # Определяем время мута
        mute_duration = None
        if warnings[target_user_id] == 5:
            mute_duration = 360  # 1 минута


        # Отправляем сообщение с количеством предупреждений
        warning_count = warnings[target_user_id]
        bot.send_message(chat_id, f"Пользователь {message.reply_to_message.from_user.first_name} получил предупреждение. Всего предупреждений: {warning_count}")

        # Если количество предупреждений достигает 3, замутить пользователя
        if mute_duration:
            mute_until[target_user_id] = time.time() + mute_duration
            bot.restrict_chat_member(chat_id, target_user_id, until_date=int(mute_until[target_user_id]), can_send_messages=False)
            bot.send_message(chat_id, f"Пользователь {message.reply_to_message.from_user.first_name} был замучен на {mute_duration // 60} минут(ы) за {warning_count} предупреждений.")
    else:
        bot.send_message(message.chat.id, "Эту команду нужно использовать как ответ на сообщение.")

# Функция мута с возможностью указать время или сделать его бесконечным
@bot.message_handler(commands=['mute'])
def mute_user(message: Message):
    if is_bot_message(message):
        bot.reply_to(message, "Нельзя влиять на бота.")
        return

    user_id = message.from_user.id
    if not has_permission(user_id, 'mute'):
        bot.reply_to(message, "У вас нет прав для использования этой команды.")
        return

    if message.reply_to_message:
        chat_id = message.chat.id
        target_user_id = message.reply_to_message.from_user.id

        # Получаем время мута из аргументов команды
        args = message.text.split()
        if len(args) == 2:
            if args[1].lower() == 'forever':
                mute_until[target_user_id] = float('inf')  # Устанавливаем бесконечный мут
                bot.restrict_chat_member(chat_id, target_user_id, until_date=None, can_send_messages=False)
                bot.send_message(chat_id, f"Пользователь {message.reply_to_message.from_user.first_name} был замучен навсегда.")
            else:
                try:
                    mute_duration = int(args[1]) * 60  # Конвертируем минуты в секунды
                    mute_until[target_user_id] = time.time() + mute_duration
                    bot.restrict_chat_member(chat_id, target_user_id, until_date=int(mute_until[target_user_id]), can_send_messages=False)
                    bot.send_message(chat_id, f"Пользователь {message.reply_to_message.from_user.first_name} был замучен на {args[1]} минут(ы).")
                except ValueError:
                    bot.send_message(message.chat.id, "Пожалуйста, введите правильное количество минут.")
        else:
            bot.send_message(message.chat.id, "Укажите количество минут или 'forever' для бесконечного мута.")
    else:
        bot.send_message(message.chat.id, "Эту команду нужно использовать как ответ на сообщение.")

# Функция бана
@bot.message_handler(commands=['ban'])
def ban_user(message: Message):
    if is_bot_message(message):
        bot.reply_to(message, "Нельзя влиять на бота.")
        return

    user_id = message.from_user.id
    if not has_permission(user_id, 'ban'):
        bot.reply_to(message, "У вас нет прав для использования этой команды.")
        return

    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        bot.kick_chat_member(chat_id, target_user_id)
        bot.send_message(chat_id, f"Пользователь {message.reply_to_message.from_user.first_name} был забанен.")
    else:
        bot.send_message(message.chat.id, "Эту команду нужно использовать как ответ на сообщение.")

# Функция размутывания
@bot.message_handler(commands=['unmute'])
def unmute_user(message: Message):
    if is_bot_message(message):
        bot.reply_to(message, "Нельзя влиять на бота.")
        return

    user_id = message.from_user.id
    if not has_permission(user_id, 'unmute'):
        bot.reply_to(message, "У вас нет прав для использования этой команды.")
        return

    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        if target_user_id in mute_until:
            if mute_until[target_user_id] == float('inf'):
                bot.restrict_chat_member(chat_id, target_user_id, until_date=None, can_send_messages=True)
                del mute_until[target_user_id]
                bot.send_message(chat_id, f"Пользователь {message.reply_to_message.from_user.first_name} был размучен.")
            elif time.time() < mute_until[target_user_id]:
                bot.restrict_chat_member(chat_id, target_user_id, until_date=None, can_send_messages=True)
                del mute_until[target_user_id]
                bot.send_message(chat_id, f"Пользователь {message.reply_to_message.from_user.first_name} был размучен.")
            else:
                bot.send_message(message.chat.id, "Время мута истекло.")
        else:
            bot.send_message(message.chat.id, "Пользователь не замучен.")
    else:
        bot.send_message(message.chat.id, "Эту команду нужно использовать как ответ на сообщение.")

# Запуск бота
bot.polling()
