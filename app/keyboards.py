from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Новости с сайта SecurityLab'),
                                      KeyboardButton(text='Новости с сайта 3DNews')],
                                     [KeyboardButton(text='Новости с сайта CNews')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')

quantity = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Новости за день', callback_data='all_news')],
                     [InlineKeyboardButton(text='Последние 5 новостей', callback_data='last_five_news')],
                     [InlineKeyboardButton(text='Свежие новости', callback_data='fresh_news')]])
