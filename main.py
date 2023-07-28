import logging
import datetime
import json
import configparser
from telegram.ext import    (InlineQueryHandler, 
                            filters,
                            PollAnswerHandler, 
                            MessageHandler, 
                            ApplicationBuilder, 
                            CommandHandler, 
                            ContextTypes,
                            CallbackQueryHandler, 
                            ApplicationBuilder, 
                            ContextTypes, 
                            CommandHandler)
from telegram import    (Update, 
                        error as TelegramError, 
                        InlineQueryResultArticle, 
                        InputTextMessageContent, 
                        InlineKeyboardButton, 
                        InlineKeyboardMarkup)




logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
class Keyboard:
    def __init__(self):
        self.DateOffset=0
        self.startDate=None
        self.endDate=None
        self.Input_End=None



    def date_picker(self):
        keyboard=[]
        for i in range(7):
            date = datetime.datetime.now() + datetime.timedelta(days=i+self.DateOffset*7)
            keyboard.append([InlineKeyboardButton(date.strftime('%Y-%m-%d'), callback_data=date.strftime('%Y-%m-%d'))])
        keyboard.append([InlineKeyboardButton('Previous', callback_data="Input_prev"),InlineKeyboardButton('Next', callback_data="Input_next")])
        return keyboard

    def overview(self):
        if self.startDate!=None and self.endDate!=None:
            keyboard = [
            [
                InlineKeyboardButton(f"Start: {self.startDate.strftime('%Y-%m-%d')}", callback_data='Input_PollStartDate'),
                InlineKeyboardButton(f"End: {self.endDate.strftime('%Y-%m-%d')}", callback_data='Input_PollEndDate'),
            ],
            [InlineKeyboardButton("Start Poll", callback_data='PollStart')],
            ]
        else:
            keyboard = [
            [
            InlineKeyboardButton("Poll Start Date", callback_data='Input_PollStartDate'),
            InlineKeyboardButton("Poll End Date", callback_data='Input_PollEndDate'),
            ]
            ]
        return (keyboard)

def get_usernames_in_group(chat_id, app:ApplicationBuilder.application_class):
    try:
        members = app.get_chat_members(chat_id)
        usernames = []

        for member in members:
            if member.user.username:
                usernames.append(member.user.username)

        return usernames
    except TelegramError as e:
        print(f"Error: ")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    await update.message.reply_text('Please choose:', reply_markup=InlineKeyboardMarkup(keyboard.overview()))

async def meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Starting Meeting!")
    await update.message.reply_text('Please choose:', reply_markup=InlineKeyboardMarkup(keyboard.overview()))


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def startPoll(query, update, context):
    text= "When meeting?"

    options=[]
    res=[]
    acc=keyboard.startDate
    while acc<=keyboard.endDate:
        if keyboard.endDate-acc==datetime.timedelta(days=11):
            for _ in range(10):
                res.append(acc.strftime('%d.%m.%Y'))
                acc+=datetime.timedelta(days=1)
            options.append(res)
            res=[]
        elif keyboard.endDate-acc>datetime.timedelta(days=10):
            for _ in range(10):
                res.append(acc.strftime('%d.%m.%Y'))
                acc+=datetime.timedelta(days=1)
            options.append(res)
            res=[]
        else:
            res.append(acc.strftime('%d.%m.%Y'))
            acc+=datetime.timedelta(days=1)
    options.append(res)
    poll_messages=[]
    payload={}
    with open("config.json", mode="w") as config:
        for i,option in enumerate(options):
            poll_messages.append(await query.get_bot().send_poll(chat_id=update.effective_chat.id, question=text, options=option, is_anonymous=False, allows_multiple_answers=True))
            payload[poll_messages[i].poll.id]={

            "questions": text,

            "number": i,

            "message_id": poll_messages[i].message_id,

            "chat_id": update.effective_chat.id,

            "answers": 0,

        }
    
    context.bot_data.update(payload)


        
            #json.dump(poll_messages[i], config)
    

async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Summarize a users poll vote"""

    answer = update.poll_answer

    print(context.bot_data)

    answered_poll = context.bot_data[answer.poll_id]

    try:

        questions = answered_poll["questions"]

    # this means this poll answer update is from an old poll, we can't do our answering then

    except KeyError:

        return

    selected_options = answer.option_ids

    await context.bot.send_message(

        answered_poll["chat_id"],
        f"{update.effective_user.id} has voted {selected_options}!",
    )

    context.bot_data["votes"]=set()

    context.bot_data["votes"].add(update.effective_user.id)

    answered_poll["answers"] += 1

    print(context.bot_data["votes"])

    # Close poll after three participants voted

    

    #await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])







async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query= update.callback_query
    print(query.data)
    print(keyboard.startDate, keyboard.endDate)
    match query.data:
        case "Input_PollStartDate":
            keyboard.Input_End=False
            await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard.date_picker()))
        case "Input_PollEndDate":
            keyboard.Input_End=True
            await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard.date_picker()))
        case "Input_next":
            keyboard.DateOffset+=1
            await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard.date_picker()))
        case "Input_prev":
            keyboard.DateOffset-=1
            await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard.date_picker()))
        case "PollStart":
            await startPoll(query, update, context)
        case _: # it is now assumed its a datestring
            if keyboard.Input_End==True:
                keyboard.endDate=datetime.datetime.strptime(query.data, '%Y-%m-%d')
            else:
                keyboard.startDate=datetime.datetime.strptime(query.data, '%Y-%m-%d')
            await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard.overview()))
    await query.answer()
#InlineKeyboardMarkup([[InlineKeyboardButton("1", callback_data="!"), InlineKeyboardButton("1", callback_data="!")],[InlineKeyboardButton("3", callback_data="25")]]))


async def handle_poll(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(update)

if __name__ == '__main__':
    config=configparser.ConfigParser()
    config.read("config.config")

    application = ApplicationBuilder().token(config["SERVER"]["API"]).build()
    
    jobs=application.job_queue
    #jobs.run_repeating(test, interval=10, first = 5)

    global keyboard
    keyboard=Keyboard()

    #inline_Meeting_handler = InlineQueryHandler(inline_Meeting)
    #application.add_handler(inline_Meeting_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    meeting_handler = CommandHandler('meeting', meeting)
    application.add_handler(meeting_handler)

    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(PollAnswerHandler(receive_poll_answer))

    #application.add_handler(PollHandler(handle_poll))#, pass_chat_data=True, pass_user_data=True))

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)



    application.run_polling()
