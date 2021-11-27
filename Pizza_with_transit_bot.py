from Modules import tokens as tk
import telebot
from telebot import types
from transitions import Machine
"""
Данный телеграм-бот принимает заказ, используя следующую схему диалога:
⎯ Какую вы хотите пиццу? Большую или маленькую?
⎯ Большую
⎯ Как вы будете платить?
⎯ Наличкой
⎯ Вы хотите большую пиццу, оплата - наличкой?
⎯ Да
⎯ Спасибо за заказ

В данном используется стейт-машина https://github.com/pytransitions/transitions

"""

BOT_TOKEN = tk.BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)

big_pizza_btn = types.InlineKeyboardButton('Большая пицца', callback_data="Большая пицца")
small_pizza_btn = types.InlineKeyboardButton('Маленькая пицца', callback_data="Маленькая пицца")
online_payment_btn = types.InlineKeyboardButton('онлайн', callback_data="онлайн")
cash_payment_btn = types.InlineKeyboardButton('наличными', callback_data="наличными")
confirm_btn = types.InlineKeyboardButton('Да', callback_data="Да")
cancel_btn = types.InlineKeyboardButton('Нет', callback_data="Нет")
question_1 = types.InlineKeyboardMarkup(row_width=1)
question_2 = types.InlineKeyboardMarkup(row_width=1)
question_3 = types.InlineKeyboardMarkup(row_width=1)
question_1.add(big_pizza_btn, small_pizza_btn)
question_2.add(online_payment_btn, cash_payment_btn)
question_3.add(confirm_btn, cancel_btn)

class Pizza_order:
    def __init__(self, size, payment):
        self.size = size
        self.payment = payment
order = Pizza_order(None,None)

states = ['order_started', 'type_of_payment_chosen', 'check_order', 'check_response', 'order_confirmed']
transitions = [
    { 'trigger': 'choose_type_of_payment', 'source': 'order_started', 'dest': 'type_of_payment_chosen' },
    { 'trigger': 'checking_order', 'source': 'type_of_payment_chosen', 'dest': 'check_order' },
    { 'trigger': 'confirm_order', 'source': 'check_order', 'dest': 'order_confirmed' },
    { 'trigger': 'order_is_confirmed', 'source': 'order_confirmed', 'dest': 'order_started' },
    { 'trigger': 'cancel_order', 'source': 'check_order', 'dest': 'order_started' }
    
]

machine = Machine(states=states, transitions=transitions, initial='order_started')

# Функция приветствия.
@bot.message_handler(content_types=['text', 'document', 'audio'])
def greeting(message):
    global mess, mark_up
    mess = message
    print('message.text  ' + message.text)
    print('machine.state  ' + machine.state)
    if message.text == '/start' and machine.state == 'order_started':
        print('start  ' + machine.state)
        greeting = "Здравствуйте! Какую вы хотите пиццу? Большую или маленькую?"
        bot.send_message(message.from_user.id, text=greeting, reply_markup=question_1)
        #machine.choose_type_of_payment()
        #bot.register_next_step_handler(message, machine.choose_type_of_payment())
    elif message.text == '/restart' and machine.state == 'order_started':
        print('restart  ' + machine.state)
        greeting = "Какую вы хотите пиццу? Большую или маленькую?"
        bot.send_message(message.from_user.id, text=greeting, reply_markup=question_1)
        #machine.choose_type_of_payment()
        #bot.register_next_step_handler(message, machine.choose_type_of_payment())
    else:
        bot.send_message(message.chat.id, 'Напишите /start')
        machine.to_order_started()
        
# Обработка кнопок inline Keyboard
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'Большая пицца' or call.data == 'Маленькая пицца':
        order.size = call.data
        machine.choose_type_of_payment()
        text = "Выбрана " + call.data
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=None)
        bot.send_message(call.message.chat.id, text="Как вы будете платить?", reply_markup=question_2)
        
    elif call.data == 'онлайн' or call.data == 'наличными':
        order.payment = call.data
        machine.checking_order()
        response = "Выбрана оплата " + call.data
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response, reply_markup=None)
        text = 'Ваш выбор: ' + order.size + ', оплата  ' + order.payment + '?'
        bot.send_message(call.message.chat.id, text=text, reply_markup=question_3)
        
    elif call.data == 'Да' or call.data == 'Нет':
        if call.data == 'Да':
                #print(call.data)
                machine.confirm_order()
                print('Заказ принят  ' + machine.state)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Спасибо! Ваш заказ принят. Если хотите выбрать новую пиццу, пропишите, пожалуйста, /restart', reply_markup=None)
                machine.order_is_confirmed()
                
        elif call.data == 'Нет':
            print(call.data)
            machine.cancel_order()
            print('до register  ' + machine.state)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сожалеем, что заказ вам не подошел. Если хотите выбрать новую пиццу, пропишите, пожалуйста, /restart', reply_markup=None)
            
            

'''
def callback_inline(call):
    #print(machine.state)
    if machine.state == 'type_of_payment_chosen':
        order.size = call.data
        #print(order.size)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Как вы будете платить?", reply_markup=question_2)
        bot.register_next_step_handler(mess, machine.checking_order())
    elif machine.state == 'check_order':
        order.payment = call.data
        text = 'Вы хотите ' + order.size + ', оплата -  ' + order.payment + '?'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=question_3)
        bot.register_next_step_handler(mess, machine.checking_response())
    elif machine.state == 'check_response':
            if call.data == 'Да':
                #print(call.data)
                bot.send_message(mess.from_user.id, 'Спасибо! Ваш заказ принят')
                machine.confirm_order()
            elif call.data == 'Нет':
                print(call.data)
                print('до register  ' + machine.state)
                bot.send_message(mess.chat.id, 'Сожалеем, что заказ вам не подошел. Если хотите выбрать новую пиццу, пропишите, пожалуйста, /restart')
                machine.cancel_order()
                
                bot.register_next_step_handler(mess,greeting)
                print('после register  ' + machine.state)
        
    elif machine.state == 'order_confirmed':
        machine.order_is_confirmed()
        #print(machine.state)
        mess == '/restart'
        bot.register_next_step_handler(mess, greeting())
'''


        
"""
def change_state():
    if machine.state == 'order_started':
        machine.choose_pizza_size()
    elif machine.state == 'choose_pizza_size':
        machine.choose_type_of_payment()
"""
    

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)