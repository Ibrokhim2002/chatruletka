import random
from aiogram import Bot, Dispatcher, types, exceptions
from aiogram.utils import executor
from aiogram.types import CallbackQuery
import mysql.connector
from chatruletka_btn import *
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import json 
from chatruletka_btn import get_buttons_for_language, get_buttons_for_language2_user, get_buttons_for_language2_partner


import aiogram.utils.exceptions

# Initialize the bot and dispatcher
bot = Bot(token="6537096284:AAFsJtNUTum_RE1CtxIg5v3Ff-kPmac8uWk")
dp = Dispatcher(bot)

# Database connection configuration
mysql_config = {
    'host': 'sql12.freemysqlhosting.net',
    'user': 'sql12732006',
    'password': 'BjaBIDqgsn',
    'database': 'sql12732006'
}

# Store chat information
pairs = {}
partner_id = None
user_language = None
partner_language = None

with open("lng.json", "r", encoding="utf-8") as file:
    messages = json.load(file)

# Handler for the /start command
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    global messages
    global user_language
    global partner_language
    global partner_id
    user_id = message.from_user.id
    username = message.from_user.username
    name = message.from_user.first_name
    surname = message.from_user.last_name

    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        # Check if the user is already in a chat
        select_query = "SELECT chat_partner FROM users WHERE user_id = %s"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)
        partner_id = mysql_cursor.fetchone()

        select_language_query = "SELECT language FROM users WHERE user_id = %s"
        select_language_values = (user_id,)
        mysql_cursor.execute(select_language_query, select_language_values)
        user_language = mysql_cursor.fetchone()

        if user_language is not None:
            user_language = user_language  # Access the language value if it's not None
        else:
            user_language = ["en0",] 

        if partner_id == None:
            partner_id = (None, )


        if partner_id[0] != None:
            await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["start_command"])
        else:
            # Check if the user is already in the users table
            select_query = "SELECT user_id FROM users WHERE user_id = %s"
            select_values = (user_id,)
            mysql_cursor.execute(select_query, select_values)
            result = mysql_cursor.fetchone()

            if not result:
                await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["send_text"])
                insert_query = "INSERT INTO users (user_id, username, name, surname, language) VALUES (%s, %s, %s, %s, %s)"
                insert_values = (user_id, username, name, surname, user_language[0])
                mysql_cursor.execute(insert_query, insert_values)
                mysql_connection.commit()

            update_query = "UPDATE users SET info = 'search' WHERE user_id = %s"
            update_values = (user_id,)
            mysql_cursor.execute(update_query, update_values)
            mysql_connection.commit()

            await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["searching"])

            # Retrieve available users from the database
            select_query = "SELECT user_id FROM users WHERE user_id != %s AND chat_partner IS NULL AND info = 'search'"
            select_values = (user_id,)
            mysql_cursor.execute(select_query, select_values)
            available_users = [result[0] for result in mysql_cursor.fetchall()]

            if available_users:
                partner_id = random.choice(available_users)

                # Update the database with the pair information
                # Assuming user_id and partner_id are the two user IDs to be paired
                update_query = "UPDATE users SET chat_partner = CASE WHEN user_id = %s THEN %s ELSE %s END WHERE user_id IN (%s, %s)"
                update_values = (user_id, partner_id, user_id, user_id, partner_id)
                mysql_cursor.execute(update_query, update_values)
                mysql_connection.commit()

                select_query = "SELECT language FROM users WHERE user_id = %s"
                select_values = (partner_id,)
                mysql_cursor.execute(select_query, select_values)
                # Fetch the result
                partner_language = mysql_cursor.fetchone()

                await bot.send_message(chat_id=partner_id, text=messages[0][partner_language[0]]["partner_found"])
                await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["partner_found"])
            else:
                pass

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()



@dp.message_handler(commands=['lng'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Please choose your language:",
                               reply_markup=buttons_column3)


@dp.callback_query_handler(lambda query: query.data in ["en0", "uz1", "ru2"])
async def handle_language(call: CallbackQuery):
    global messages

    user_id = call.from_user.id
    language = call.data

    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        # Update the user's language preference in the database
        update_query = "UPDATE users SET language = %s WHERE user_id = %s"
        update_values = (language, user_id)
        mysql_cursor.execute(update_query, update_values)
        mysql_connection.commit()

        select_query = "SELECT language FROM users WHERE user_id = %s"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)

        # Fetch the result
        result = mysql_cursor.fetchone()
        


        with open("lng.json", "r", encoding="utf-8") as file:
            messages = json.load(file)
            
        
        # Provide a confirmation message
        await bot.send_message(chat_id=user_id, text=messages[0][language]["language_confirmation"])

      
    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()




@dp.message_handler(commands=['next'])
async def next_command(message: types.Message):
    global messages
    global user_language
    global partner_language
    user_id = message.from_user.id
    

    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        # Retrieve the current user's chat partner from the database
        select_query = "SELECT chat_partner FROM users WHERE user_id = %s"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)
        partner_id = mysql_cursor.fetchone()[0]

        select_query = "SELECT language FROM users WHERE user_id = %s"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)
        # Fetch the result
        user_language = mysql_cursor.fetchone()

        select_query = "SELECT language FROM users WHERE user_id = %s"
        select_values = (partner_id,)
        mysql_cursor.execute(select_query, select_values)
        # Fetch the result
        partner_language = mysql_cursor.fetchone()

        buttons2_user = get_buttons_for_language2_user(user_language[0])
        

        if partner_id:
            buttons2_partner = get_buttons_for_language2_partner(partner_language[0])
            await bot.send_message(chat_id=partner_id, text=messages[0][partner_language[0]]["stopped_dialog_partner"])
            await bot.send_message(chat_id=partner_id, text=messages[0][partner_language[0]]["feedback_message"], reply_markup=buttons2_partner)
            await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["feedback_message"], reply_markup=buttons2_user)

        # Clear the chat information for the current user and their partner
        update_query = "UPDATE users SET chat_partner = NULL, info = NULL WHERE user_id IN (%s, %s)"
        update_values = (user_id, partner_id)
        mysql_cursor.execute(update_query, update_values)
        mysql_connection.commit()

        # Update the info column for the user who gives the /next command
        update_query = "UPDATE users SET info = 'search' WHERE user_id = %s"
        update_values = (user_id,)
        mysql_cursor.execute(update_query, update_values)
        mysql_connection.commit()

        # Retrieve available users from the database
        select_query = "SELECT user_id FROM users WHERE user_id != %s AND chat_partner IS NULL AND info = 'search'"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)
        available_users = [result[0] for result in mysql_cursor.fetchall()]

        await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["searching"])

        if available_users:
            partner_id = random.choice(available_users)

            # Update the database with the pair information
            # Assuming user_id and partner_id are the two user IDs to be paired
            update_query = "UPDATE users SET chat_partner = CASE WHEN user_id = %s THEN %s ELSE %s END WHERE user_id IN (%s, %s)"
            update_values = (user_id, partner_id, user_id, user_id, partner_id)
            mysql_cursor.execute(update_query, update_values)
            mysql_connection.commit()

            select_query = "SELECT language FROM users WHERE user_id = %s"
            select_values = (partner_id,)
            mysql_cursor.execute(select_query, select_values)
            # Fetch the result
            partner_language = mysql_cursor.fetchone()

            await bot.send_message(chat_id=partner_id, text=messages[0][partner_language[0]]["partner_found"])
            await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["partner_found"])
        else:
            pass

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()



@dp.message_handler(commands=['stop'])
async def stopchat_command(message: types.Message):
    global messages
    user_id = message.from_user.id

    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        # Retrieve chat partner's ID and language from the database
        select_query = "SELECT chat_partner, language FROM users WHERE user_id = %s"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)
        result = mysql_cursor.fetchone()
        

        # Check if the user is in a chat and get partner's ID and language
        if result[0]!=None:
            partner_id, user_language = result[0], result[1]

            # Fetch the language of the partner
            partner_language = fetch_partner_language(mysql_cursor, partner_id)

            # Clear the chat information in the database
            update_query = "UPDATE users SET chat_partner = NULL, info = NULL WHERE user_id IN (%s, %s)"
            update_values = (user_id, partner_id)
            mysql_cursor.execute(update_query, update_values)
            mysql_connection.commit()


            # Send messages to the user and partner
            if messages and user_language in messages[0]:
                buttons2_user = get_buttons_for_language2_user(user_language)
                await bot.send_message(chat_id=user_id, text=messages[0][user_language]["stopped_dialog_user"])
                await bot.send_message(chat_id=user_id, text=messages[0][user_language]["feedback_message"], reply_markup=buttons2_user)
            if partner_id and partner_language and partner_language in messages[0]:
                buttons2_partner = get_buttons_for_language2_partner(partner_language)
                await bot.send_message(chat_id=partner_id, text=messages[0][partner_language]["stopped_dialog_partner"])
                await bot.send_message(chat_id=partner_id, text=messages[0][partner_language]["feedback_message"], reply_markup=buttons2_partner)
        else:
            partner_id, user_language = result[0], result[1]
            partner_language = fetch_partner_language(mysql_cursor, partner_id)
            await bot.send_message(chat_id=user_id, text=messages[0][user_language]["no_partner"])

    except exceptions.ChatIdIsEmpty:
        return

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()

# Function to fetch the language of the partner
def fetch_partner_language(cursor, partner_id):
    select_language_query = "SELECT language FROM users WHERE user_id = %s"
    select_language_values = (partner_id,)
    cursor.execute(select_language_query, select_language_values)
    partner_language = cursor.fetchone()
    return partner_language[0] if partner_language else None


navigation_stack = []

@dp.callback_query_handler(text="cool")
async def btn(call: CallbackQuery):
    global user_language
    global partner_language
    global messages
    user_id = call.from_user.id 
    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        select_language_query = "SELECT language FROM users WHERE user_id = %s"
        select_language_values = (user_id,)
        mysql_cursor.execute(select_language_query, select_language_values)
        user_language = mysql_cursor.fetchone()
        
        await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=messages[0][user_language[0]]["thanks_feedback"])

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()

@dp.callback_query_handler(text="fuu")
async def btn(call: CallbackQuery):
    global user_language
    global partner_language
    global messages
    user_id = call.from_user.id 
    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        select_language_query = "SELECT language FROM users WHERE user_id = %s"
        select_language_values = (user_id,)
        mysql_cursor.execute(select_language_query, select_language_values)
        user_language = mysql_cursor.fetchone()

        await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=messages[0][user_language[0]]["thanks_feedback"])

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()

@dp.callback_query_handler(text="report")
async def btn(call: CallbackQuery):
    global user_language
    global partner_language
    global messages
    user_id = call.from_user.id 
    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        select_language_query = "SELECT language FROM users WHERE user_id = %s"
        select_language_values = (user_id,)
        mysql_cursor.execute(select_language_query, select_language_values)
        user_language = mysql_cursor.fetchone()

        buttons = get_buttons_for_language(user_language)

        await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=messages[0][user_language[0]]["choose_reason"], reply_markup=buttons)
        # Save the current menu for navigation
        if buttons not in navigation_stack:
            navigation_stack.append(buttons)

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()

@dp.callback_query_handler(text="back")
async def btn(call: CallbackQuery):
    global user_language
    global partner_language
    global messages
    user_id = call.from_user.id 
    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        select_language_query = "SELECT language FROM users WHERE user_id = %s"
        select_language_values = (user_id,)
        mysql_cursor.execute(select_language_query, select_language_values)
        user_language = mysql_cursor.fetchone()
 

        if navigation_stack:
            buttons2 = get_buttons_for_language2_user(user_language[0])
            previous_menu = navigation_stack.pop()
            await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=messages[0][user_language[0]]["back_menu"], reply_markup=buttons2)

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()

@dp.callback_query_handler(lambda query: query.data in ["advertise", "selling", "child_porn", "begging", "insulting", "violance", "vulgar"])
async def handle_reason(call: CallbackQuery):
    global user_language
    global partner_language
    global messages
    user_id = call.from_user.id 
    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        select_language_query = "SELECT language FROM users WHERE user_id = %s"
        select_language_values = (user_id,)
        mysql_cursor.execute(select_language_query, select_language_values)
        user_language = mysql_cursor.fetchone()

        await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=messages[0][user_language[0]]["thanks_feedback"])

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()
    



@dp.message_handler(commands=['search'])
async def start_command(message: types.Message):
    global user_language
    global partner_language
    global messages
    user_id = message.from_user.id

    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        # Check if the user is already in a chat
        select_query = "SELECT chat_partner FROM users WHERE user_id = %s"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)
        partner_id = mysql_cursor.fetchone()

        select_language_query = "SELECT language FROM users WHERE user_id = %s"
        select_language_values = (user_id,)
        mysql_cursor.execute(select_language_query, select_language_values)
        user_language = mysql_cursor.fetchone()

        if partner_id == None:
            partner_id = (None, )


        if partner_id[0] != None:
            await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["start_command"])
        else:
            # Check if the user is already in the users table
            select_query = "SELECT user_id FROM users WHERE user_id = %s"
            select_values = (user_id,)
            mysql_cursor.execute(select_query, select_values)
            result = mysql_cursor.fetchone()

            if not result:
                insert_query = "INSERT INTO users (user_id) VALUES (%s)"
                insert_values = (user_id,)
                mysql_cursor.execute(insert_query, insert_values)
                mysql_connection.commit()

            update_query = "UPDATE users SET info = 'search' WHERE user_id = %s"
            update_values = (user_id,)
            mysql_cursor.execute(update_query, update_values)
            mysql_connection.commit()

            await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["searching"])

            # Retrieve available users from the database
            select_query = "SELECT user_id FROM users WHERE user_id != %s AND chat_partner IS NULL AND info = 'search'"
            select_values = (user_id,)
            mysql_cursor.execute(select_query, select_values)
            available_users = [result[0] for result in mysql_cursor.fetchall()]

            if available_users:
                partner_id = random.choice(available_users)

                # Update the database with the pair information
                # Assuming user_id and partner_id are the two user IDs to be paired
                update_query = "UPDATE users SET chat_partner = CASE WHEN user_id = %s THEN %s ELSE %s END WHERE user_id IN (%s, %s)"
                update_values = (user_id, partner_id, user_id, user_id, partner_id)
                mysql_cursor.execute(update_query, update_values)
                mysql_connection.commit()

                select_query = "SELECT language FROM users WHERE user_id = %s"
                select_values = (partner_id,)
                mysql_cursor.execute(select_query, select_values)
                # Fetch the result
                partner_language = mysql_cursor.fetchone()

                await bot.send_message(chat_id=partner_id, text=messages[0][partner_language[0]]["partner_found"])
                await bot.send_message(chat_id=user_id, text=messages[0][user_language[0]]["partner_found"])
            else:
                pass

    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)

    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()





@dp.message_handler(content_types=[
    types.ContentType.TEXT,
    types.ContentType.VIDEO,
    types.ContentType.PHOTO,
    types.ContentType.VOICE,
    types.ContentType.VIDEO_NOTE,
    types.ContentType.AUDIO,
    types.ContentType.ANIMATION

])
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    try:
        mysql_connection = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_connection.cursor()

        # Retrieve chat partner's ID from the database
        select_query = "SELECT chat_partner FROM users WHERE user_id = %s"
        select_values = (user_id,)
        mysql_cursor.execute(select_query, select_values)
        partner_id = mysql_cursor.fetchone()

        if partner_id:
            partner_id = partner_id[0]  # Extract the partner ID from the tuple
            content_type = message.content_type

            if message.reply_to_message:
                replied_message = message.reply_to_message

                if content_type == types.ContentType.TEXT:
                    try:
                        # Attempt to send the message as a reply
                        await bot.send_message(chat_id=partner_id, text=message.text, reply_to_message_id=message.reply_to_message.message_id-1)
                    except aiogram.utils.exceptions.BadRequest as e:
                        if "Replied message not found" in str(e):
                            # Handle the "Replied message not found" error by sending a regular message
                            await bot.send_message(chat_id=partner_id, text=message.text)
                elif content_type == types.ContentType.PHOTO:
                    # Send a photo with a reference to the replied message
                    photo = message.photo[-1]  # Get the largest available photo
                    try:
                        await bot.send_photo(chat_id=partner_id, photo=photo.file_id, reply_to_message_id=message.reply_to_message.message_id-1)
                    except aiogram.utils.exceptions.BadRequest as e:
                        if "Replied message not found" in str(e):
                            # Handle the "Replied message not found" error by sending a regular message
                            await bot.send_photo(chat_id=partner_id, photo=photo.file_id)
                elif content_type == types.ContentType.VIDEO:
                    # Send video with a reference to the replied message
                    try:
                        await bot.send_video(chat_id=partner_id, video=message.video.file_id, reply_to_message_id=message.reply_to_message.message_id-1)
                    except aiogram.utils.exceptions.BadRequest as e:
                        if "Replied message not found" in str(e):
                            # Handle the "Replied message not found" error by sending a regular message
                            await bot.send_video(chat_id=partner_id, video=message.video.file_id)
                elif content_type == types.ContentType.VOICE:
                    # Send audio with a reference to the replied message
                    try:
                        await bot.send_voice(chat_id=partner_id, voice=message.voice.file_id, reply_to_message_id=message.reply_to_message.message_id-1)
                    except aiogram.utils.exceptions.BadRequest as e:
                        if "Replied message not found" in str(e):
                            # Handle the "Replied message not found" error by sending a regular message
                            await bot.send_voice(chat_id=partner_id, voice=message.voice.file_id)
                elif content_type == types.ContentType.VIDEO_NOTE:
                    # Send video note with a reference to the replied message
                    try:
                        await bot.send_video_note(chat_id=partner_id, video_note=message.video_note.file_id, reply_to_message_id=message.reply_to_message.message_id-1)
                    except aiogram.utils.exceptions.BadRequest as e:
                        if "Replied message not found" in str(e):
                            # Handle the "Replied message not found" error by sending a regular message
                            await bot.send_video_note(chat_id=partner_id, video_note=message.video_note.file_id)
                elif content_type == types.ContentType.AUDIO:
                    # Send audio with a reference to the replied message
                    try:
                        await bot.send_audio(chat_id=partner_id, audio=message.audio.file_id, reply_to_message_id=message.reply_to_message.message_id-1)
                    except aiogram.utils.exceptions.BadRequest as e:
                        if "Replied message not found" in str(e):
                            # Handle the "Replied message not found" error by sending a regular message
                            await bot.send_audio(chat_id=partner_id, audio=message.audio.file_id)
                elif content_type == types.ContentType.ANIMATION:
                    # Send animation (GIF) with a reference to the replied message
                    try:
                        await bot.send_animation(chat_id=partner_id, animation=message.animation.file_id, reply_to_message_id=message.reply_to_message.message_id-1)
                    except aiogram.utils.exceptions.BadRequest as e:
                        if "Replied message not found" in str(e):
                            # Handle the "Replied message not found" error by sending a regular message
                            await bot.send_animation(chat_id=partner_id, animation=message.animation.file_id)
            else:
                # Handle messages that are not replies
                if content_type == types.ContentType.TEXT:
                    # Send text message
                    await bot.send_message(chat_id=partner_id, text=message.text)
                elif content_type == types.ContentType.PHOTO:
                    # Send photo
                    photo = message.photo[-1]  # Get the largest available photo
                    await bot.send_photo(chat_id=partner_id, photo=photo.file_id)
                elif content_type == types.ContentType.VIDEO:
                    # Send video
                    await bot.send_video(chat_id=partner_id, video=message.video.file_id)
                elif content_type == types.ContentType.VOICE:
                    # Send audio
                    await bot.send_voice(chat_id=partner_id, voice=message.voice.file_id)
                elif content_type == types.ContentType.VIDEO_NOTE:
                    # Send video note
                    await bot.send_video_note(chat_id=partner_id, video_note=message.video_note.file_id)
                elif content_type == types.ContentType.AUDIO:
                    # Send audio
                    await bot.send_audio(chat_id=partner_id, audio=message.audio.file_id)
                elif content_type == types.ContentType.ANIMATION:
                    # Send animation (GIF)
                    await bot.send_animation(chat_id=partner_id, animation=message.animation.file_id)
        else:
            pass
    except mysql.connector.Error as error:
        print('Error connecting to the database:', error)
    except Exception as e:
        pass
    finally:
        if mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()






# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
