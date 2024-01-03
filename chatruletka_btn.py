from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json


with open("lng.json", "r", encoding="utf-8") as file:
        messages = json.load(file)

def get_buttons_for_language2_user(user_language):
    buttons_column2 = InlineKeyboardMarkup(row_width=2)
    buttons_column2.add(
        InlineKeyboardButton("👍", callback_data="cool"),
        InlineKeyboardButton("👎", callback_data="fuu"),
        InlineKeyboardButton(messages[0][user_language]["report"], callback_data="report")
    )
    return buttons_column2

def get_buttons_for_language2_partner(user_language):
    buttons_column2 = InlineKeyboardMarkup(row_width=2)
    buttons_column2.add(
        InlineKeyboardButton("👍", callback_data="cool"),
        InlineKeyboardButton("👎", callback_data="fuu"),
        InlineKeyboardButton(messages[0][user_language]["report"], callback_data="report")
    )
    return buttons_column2


def get_buttons_for_language(language):
    buttons_column1 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["advertising"], callback_data='advertise'),
            ],
            [
                InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["selling"], callback_data='selling'),
            ],
            [
                InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["child_porn"], callback_data='child_porn'),
            ],
            [
    		    InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["begging"], callback_data='begging'),
            ],
            [
                InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["insulting"], callback_data='insulting'),
            ],
            [
                InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["violance"], callback_data='violance'),
            ],
            [
                InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["vulgar"], callback_data='vulgar'),
            ],
            [  
                InlineKeyboardButton(messages[0][language[0]]["buttons_column1"]["back"], callback_data='back'),
            ],
        ]
    )
    return buttons_column1
   

buttons_column3 = InlineKeyboardMarkup(row_width=3)
buttons_column3.add(
    InlineKeyboardButton("🇺🇿 Uzbek", callback_data="uz1"),
    InlineKeyboardButton("🇷🇺 Russian", callback_data="ru2"),
    InlineKeyboardButton("🇬🇧 English", callback_data="en0")
)
