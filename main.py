#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

# from requests_forwarder import setup_proxy
# setup_proxy(
#     proxy_token="",
# )

import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
import random
from Texts import texts
import threading
from DML import insert_product_data
from DQL import get_categories, get_products_by_cat, get_products_by_id


os.makedirs('Data', exist_ok=True)

user_steps = dict()     # {cid: step, ...}
user_data = dict()      # {cid: {'first_name': first_name, 'last_name': last_name}, ...}
shopping_cart = dict()  # {cid: {pid: qty}, ...}


API_TOKEN = os.environ.get('Telegram_API_TOKEN')
DESC_CHANNEL_CID = -1003893003326
STORE_CHANNEL_CID = -1003730955174
SUPPORT_CID = 8082244374
SECRET = 986234823
admins = [8082244374]
spam_data = dict()    # {cid: {'last_message_time': float, score: int}, ...}
spam_users = list()   # [cid, ...]
lower_bond, upper_bond, spam_limit = 2, 5, 50


commands = {
    'start'                 :       'start the bot',
    'help'                  :       'get information about bot',
    'keyboard'              :       'send sample reply keyboard',
    'get_info'              :       'get information from user',
    'send_photo'            :       'send sample photo',
    'send_doc'              :       'send sample document',
    'send_inline_keybaord'  :       'send sample inline keyboard',
    'show_product'          :       'send product picture with information',
    'edit_text'             :       'send text message and edit it',
    'delete_message'        :       'send message and then delete it',
    'markdown'              :       'send sample message with markdown style',
    'support'               :       'send support contact info',
    'invite_link'           :       'create and send user\'s invite link',
    'request_contact'       :       'request user to send its number',
    'all_products'          :       'send all products info',
}

admin_commands = {
    'add_product'           :       'send product info by admin and save to database',
}

message_ids = {
    'start'     :   [3, 5],
}


bot = telebot.TeleBot(API_TOKEN)

hideboard = ReplyKeyboardRemove()

# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        # print(m)
        if m.content_type == 'text':
            # print the sent message to the console
            print(f"{m.chat.first_name} [{m.chat.id}]: {m.text}")
        elif m.content_type == 'photo':
            # print the sent message to the console
            print(f"{m.chat.first_name} [{m.chat.id}]: new photo recieved")
        elif m.content_type == 'document':
            # print the sent message to the console
            print(f"{m.chat.first_name} [{m.chat.id}]: new document recieved")

def send_message(*args, **kwargs):
    try:
        return bot.send_message(*args, **kwargs)
    except Exception as e:
        pass

def encrypt_cid(cid):
    return str(random.randint(10, 99)) + str((cid + SECRET) * 2) + str(random.randint(10, 99))    

def decrypt_cid(invite_value):
    return int(invite_value[2:-2]) // 2 - SECRET

def gen_product_message_markup(pid, qty):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('➖', callback_data=f'change_{pid}_{qty-1}'),
               InlineKeyboardButton(str(qty), callback_data='nothing'),
               InlineKeyboardButton('➕', callback_data=f'change_{pid}_{qty+1}'))
    markup.add(InlineKeyboardButton('Add to basket', callback_data=f'add_{pid}_{qty}'))
    markup.add(InlineKeyboardButton('Cancel', callback_data='cancel'))
    return markup

def safe(string):
    return str(string).replace('*', r'\*').replace('_', r'\_').replace('|', r'\|').replace('.', r'\.')

def gen_product_caption(product_info, for_channel=False):
    text = f"""product information
*name*: {safe(product_info['name'])}
*description*: {safe(product_info['description'])}
*price*: {safe(product_info['price'])}\n"""
    if for_channel:
        text += safe(f"[Buy](https://t.me/Python_class3_bot?start=show_product_{product_info['id']})")
    return text

def is_spam(cid):
    global spam_data, spam_users
    if cid not in spam_data:
        spam_data.setdefault(cid, {'last_message_time': time.time() , 'score': 0})
        return False
    if cid in spam_users:
        return True
    last_message_time = time.time()
    if last_message_time - spam_data[cid]['last_message_time'] < lower_bond:
        spam_data[cid]['score'] += 1
    elif last_message_time - spam_data[cid]['last_message_time'] > upper_bond:
        spam_data[cid]['score'] = max(0, spam_data[cid]['score']-1)
    if spam_data[cid]['score'] >= spam_limit:
        spam_users.append(cid)
        return True
    return False
    
def update_spam_list():
    print('update_spam_list function called')
    
def worker():
    while True:
        update_spam_list()
        time.sleep(60)    


bot.set_update_listener(listener)  # register listener


@bot.callback_query_handler(func=lambda call: True)
def callbakc_handler(call):
    call_id = call.id
    cid = call.message.chat.id
    if is_spam(cid): return
    mid = call.message.message_id
    data = call.data
    print(f'call id: {call_id}, cid: {cid}, mid: {mid}, data: {data}')
    if data == 'data 1':
        bot.answer_callback_query(call_id, 'this is answer')
        send_message(cid, 'you pressed button 1')
    elif data == 'data 2':
        bot.answer_callback_query(call_id, 'this is answer')
        send_message(cid, 'you pressed button 2')
    elif data.startswith('change'):
        _, pid, qty = data.split('_')
        if qty == '0':
            bot.answer_callback_query(call_id, 'qunantity can not be zero')
            return
        bot.answer_callback_query(call_id, f'change quantity to {qty}')
        bot.edit_message_reply_markup(cid, mid, reply_markup=gen_product_message_markup(int(pid), int(qty)))
    elif data.startswith('add'):
        _, pid, qty = data.split('_')
        shopping_cart.setdefault(cid, dict())
        shopping_cart[cid].setdefault(int(pid), 0)
        shopping_cart[cid][int(pid)] += int(qty)
        bot.answer_callback_query(call_id, f'product {pid} added to basket: {qty}')
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        print(shopping_cart)
    elif data.startswith('answer'):
        customer_cid = int(data.split('_')[-1])
        user_steps[cid] = 'answser'
        user_data[cid] = customer_cid
        bot.answer_callback_query(call_id, f'send your answer to: {customer_cid}')
        send_message(cid, f'send your answer to: {customer_cid}')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('✅ answer', callback_data=f'nothing'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    elif data.startswith('show_cat'):
        category = data.split('_')[-1]
        products = get_products_by_cat(category)
        target_products = products[0]
        bot.send_photo(cid, target_products['file_id'], caption=gen_product_caption(target_products), reply_markup=gen_product_message_markup(target_products['id'], 1), parse_mode='MarkdownV2')
        bot.answer_callback_query(call_id, f'show product id: {target_products["id"]}')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'✅ {category}', callback_data=f'nothing'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    elif data == 'nothing':
        bot.answer_callback_query(call_id, 'nothing')
        

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    if is_spam(cid): return
    text = message.text
    if len(text.split()) > 1:
        invite_value = text.split()[-1]
        if invite_value.startswith('show_product_'):
            product_id = int(invite_value.split('_')[-1])
            product_info = get_products_by_id(product_id)
            bot.send_photo(cid, product_info['file_id'], caption=gen_product_caption(product_info),   reply_markup=gen_product_message_markup(product_info['id'], 1), parse_mode='MarkdownV2')
    else:
        mid = random.choice(message_ids['start'])
        bot.copy_message(cid, DESC_CHANNEL_CID, mid, reply_to_message_id=message.message_id)

@bot.message_handler(commands=['help'])
def command_help_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    text = "here is bot commands:\n"
    for command, desc in commands.items():
        text += f"/{command} - {desc}\n"
    if cid in admins:
        text += "******here is admin commands******\n"
        for command, desc in admin_commands.items():
            text += f"/{command} - {desc}\n"        
    send_message(cid, text)

@bot.message_handler(commands=['keyboard'])
def command_keyboard_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(texts['button 1'], texts['button 2'])
    send_message(cid, 'بفرمائید این کیبرد شما است:', reply_markup=keyboard)
    send_message(cid, texts['credit'].format(100))
    
@bot.message_handler(commands=['get_info'])
def command_get_info_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    send_message(cid, 'please enter your first name:')
    user_steps[cid] = "X"

@bot.message_handler(commands=['send_photo'])
def command_send_photo_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    # bot.send_photo(cid, "AgACAgQAAxkBAANaaYROSzrTG7zAyBjSYkwSgNNIxqcAAu8Maxsc2SFQdvibukyssbYBAAMCAANtAAM4BA")
    # bot.send_photo(cid, "https://imgs.xkcd.com/comics/solar_spectrum.png")
    with open(r"Data\Photo\8082244374\1770274258.960248.jpg", 'rb') as f:
        bot.send_photo(cid, f)
    
@bot.message_handler(commands=['send_doc'])
def command_send_doc_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    with open(r"Data\Photo\8082244374\1770274258.960248.jpg", 'rb') as f:
        bot.send_document(cid, f)

@bot.message_handler(commands=['send_inline_keybaord'])
def command_send_inline_keybaord_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('button 1', callback_data='data 1'))
    markup.add(InlineKeyboardButton('button 2', callback_data='data 2'))
    send_message(cid, 'here is your keyboard', reply_markup=markup)


@bot.message_handler(commands=['show_product'])
def command_show_product_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    all_products = get_products_by_cat('shoe')
    bot.send_photo(cid, all_products[0]['file_id'], caption=gen_product_caption(all_products[0]), reply_markup=gen_product_message_markup(all_products[0]['id'], 1), parse_mode='MarkdownV2')

@bot.message_handler(commands=['edit_text'])
def command_edit_text_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    sent_message = send_message(cid, 'this is sample message')
    time.sleep(2)
    bot.edit_message_text('this is edited message', cid, sent_message.message_id)

@bot.message_handler(commands=['delete_message'])
def command_delete_message_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    sent_message = send_message(cid, 'this is sample message')
    time.sleep(2)
    bot.delete_message(cid, sent_message.message_id)

@bot.message_handler(commands=['markdown'])
def command_markdown_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    text = "this is *bold* _italic_ __underlined__ ||spoiler||\nclick [Here](https://google.com)"
    send_message(cid, text, parse_mode='MarkdownV2')

@bot.message_handler(commands=['support'])
def command_support_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    send_message(cid, f'You can send your message to [Support](tg://user?id={SUPPORT_CID}), or send your message here:', parse_mode='MarkdownV2')
    user_steps[cid] = 'Support'

@bot.message_handler(commands=['invite_link'])
def command_invite_link_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    send_message(cid, f'here is your invite link: https://t.me/Python_class3_bot?start={cid}')

@bot.message_handler(commands=['request_contact'])
def command_request_contact_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('send your number', request_contact=True))
    keyboard.add(KeyboardButton('send your location', request_location=True))
    send_message(cid, 'please share your information:', reply_markup=keyboard)

@bot.message_handler(commands=['all_products'])
def command_all_products_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    cats = get_categories()
    markup = InlineKeyboardMarkup()
    for cat in cats:
        markup.add(InlineKeyboardButton(cat, callback_data=f'show_cat_{cat}'))
    bot.send_message(cid, 'please select one category', reply_markup=markup)    

@bot.message_handler(commands=['add_product'])
def command_add_product_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    if cid in admins:
        bot.send_message(cid, """please send product pricture and caption as follows:
name: product name
desc: product description
price: product price
category: product category
inventory: product inventory""")
        user_steps[cid] = 'AP'
    else:
        echo_message(message)

@bot.message_handler(func=lambda message: message.text.startswith('button'))
def keyboard_button_1_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    button_no = int(message.text.split()[-1])
    send_message(cid, f'you pressed button {button_no}', reply_markup=hideboard)

@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'X')
def user_step_x_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    first_name = message.text
    user_data.setdefault(cid, {'first_name': None, 'last_name': None})
    user_data[cid]['first_name'] = first_name
    send_message(cid, 'please enter your last name:')
    user_steps[cid] = "Y"
    
@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'Y')
def user_step_y_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    last_name = message.text
    user_data.setdefault(cid, {'first_name': None, 'last_name': None})
    user_data[cid]['last_name']  = last_name
    send_message(cid, f"your full name is: {user_data[cid]['first_name']} {user_data[cid]['last_name']}")
    user_steps.pop(cid)
    
@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'Support')
def user_step_Support_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    forwarded_message = bot.forward_message(SUPPORT_CID, cid, message.message_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('answer', callback_data=f'answer_{cid}'))
    send_message(SUPPORT_CID, 'click below button to answer', reply_markup=markup, reply_to_message_id=forwarded_message.message_id)
    send_message(cid, 'thank you for your message')
    user_steps.pop(cid)

@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'answser')
def user_step_Support_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    customer_cid = user_data.get(cid)
    bot.copy_message(customer_cid, cid, message.message_id)
    send_message(cid, f'your message has sent to [USER](tg://user?id={customer_cid})', parse_mode='MarkdownV2')
    user_data.pop(cid)
    

    
@bot.message_handler(content_types=['document'])
def content_type_document_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    content = bot.download_file(file_path)
    os.makedirs(os.path.join('Data', 'Document', str(cid)), exist_ok=True)
    file_save_path = os.path.join('Data', 'Document', str(cid), file_name)
    with open(file_save_path, 'wb') as f:
        f.write(content)


@bot.message_handler(content_types=['photo'])
def content_type_photo_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    if user_steps.get(cid) == "AP":
        file_id = message.photo[-1].file_id
        caption = message.caption
        try:
            info = caption.split('\n')
            product_name = info[0].split(':', 1)[-1].strip()
            product_desc = info[1].split(':', 1)[-1].strip()
            product_price = float(info[2].split(':', 1)[-1].strip())
            product_cat = info[3].split(':', 1)[-1].strip().lower()
            if product_cat not in ('shoe', 'bag', 'accessory'):
                raise TypeError('invalif category info')
            product_inv = int(info[4].split(':', 1)[-1].strip())
        except Exception:
            bot.send_message(cid, 'invalid caption format')
        else:
            product_id = insert_product_data(product_name, product_desc, product_cat, product_price, product_inv, file_id)
            bot.send_message(cid, f'product insert successfully with id: {product_id}')
            product_info = get_products_by_id(product_id)
            bot.send_photo(STORE_CHANNEL_CID, file_id, caption=gen_product_caption(product_info, for_channel=True), parse_mode='MarkdownV2')
    else:
        bot.send_message(cid, 'please use commands first')
        # file_id = message.photo[-1].file_id
        # # print(file_id)
        # file_info = bot.get_file(file_id)
        # file_path = file_info.file_path
        # content = bot.download_file(file_path)
        # extension = file_path.split('.')[-1]
        # os.makedirs(os.path.join('Data', 'Photo', str(cid)), exist_ok=True)
        # file_save_path = os.path.join('Data', 'Photo', str(cid), f'{time.time()}.{extension}')
        # with open(file_save_path, 'wb') as f:
        #     f.write(content)

@bot.message_handler(content_types=['contact'])
def content_conact_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    user_number = message.contact.phone_number
    user_cid = message.contact.user_id
    if user_cid == cid:
        send_message(cid, f'your number {user_number} was approved')
    else:
        send_message(cid, 'please share your real number')

@bot.message_handler(content_types=['location'])
def content_location_handler(message):
    cid = message.chat.id
    if is_spam(cid): return
    print(message.location)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    cid = message.chat.id
    if is_spam(cid): return
    bot.reply_to(message, f"invalid input: {message.text}. you can use /help menu.")


worker_thread = threading.Thread(target=worker)
worker_thread.start()

bot.infinity_polling()