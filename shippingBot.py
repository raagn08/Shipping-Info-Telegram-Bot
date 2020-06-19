from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, Handler
from telegram.ext.dispatcher import run_async, DispatcherHandlerStop, Dispatcher
from telegram import Update, User, Message, ParseMode
from telegram.error import BadRequest
import requests_html
import requests
import json
import logging

#Enter API-KEY here
updater = Updater("API-KEY", use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(filename="shipping.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#Tracking Function for E-Kart Logistics
@run_async
def ekart(update: Update, context: CallbackContext):
    if update.message!=None:
        trackingID = (update.message.text).split()[1]
        data = []
        session = requests_html.HTMLSession()
        response = session.get("https://ekartlogistics.com/track/"+str(trackingID)+"/")
        for selector in response.html.xpath('//div[@id="no-more-tables"][1]/table/tbody'):
            data.append(selector.text)

        context.bot.send_message(chat_id=update.effective_chat.id, text="*Shipping Status: *\n\n`Latest Status: "+data[0]+"`\n\n*Tracking Info:*\n\n`"+data[1]+"`", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.MARKDOWN)

#Tracking Function for Pitney Bowes  
@run_async
def pitneyb(update: Update, context: CallbackContext):
    if update.message!=None:
        trackingID = (update.message.text).split()[1]
        response = requests.get("https://parceltracking.pb.com/ptsapi/track-packages/"+trackingID)
        jsonData = json.loads(response.text)
        try:
            currentStatusData = [
                'Status: '+jsonData['currentStatus']['packageStatus'],
                'Last Updated: '+jsonData['currentStatus']['eventDate']+' '+jsonData['currentStatus']['eventTime'],
                'Description: '+jsonData['currentStatus']['eventDescription'],
                'Location: '+jsonData['currentStatus']['eventLocation']['city']+", "+jsonData['currentStatus']['eventLocation']['countyOrRegion']+' - '+jsonData['currentStatus']['eventLocation']['postalOrZipCode']
            ]
        except KeyError:
            currentStatusData = [
                'Status: '+jsonData['currentStatus']['packageStatus'],
                'Last Updated: '+jsonData['currentStatus']['eventDate']+' '+jsonData['currentStatus']['eventTime'],
                'Description: '+jsonData['currentStatus']['eventDescription'],
                'Location: '+jsonData['currentStatus']['eventLocation']['city']+", "+jsonData['currentStatus']['eventLocation']['countyOrRegion']+' - '
            ]
        currentStatusData = "\n".join(currentStatusData)

        history = []
        for x in jsonData['scanHistory']['scanDetails']:
            try:
                history.append([
                'Status: '+x['packageStatus'],
                'Last Updated: '+x['eventDate']+' '+x['eventTime'],
                'Description: '+x['eventDescription'],
                'Location: '+x['eventLocation']['city']+", "+x['eventLocation']['countyOrRegion']+' - '+x['eventLocation']['postalOrZipCode']
            ])
            except KeyError:
                history.append([
                'Status: '+x['packageStatus'],
                'Last Updated: '+x['eventDate']+' '+x['eventTime'],
                'Description: '+x['eventDescription'],
            ])
        
        historyData = []
        for i in range(len(history)):
            historyData.append("\n".join(history[i]))
        
        historyData = "\n\n".join(historyData)
        
        context.bot.send_message(chat_id=update.effective_chat.id, text="*Shipping Status: *\n\n`Latest Status:\n"+currentStatusData+"`\n\n*Tracking Info:*\n\n`"+historyData+"`", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.MARKDOWN)

#Tracking Function for Canada Post
@run_async
def canadapost(update: Update, context: CallbackContext):
    if update.message!=None:
        trackingID = (update.message.text).split()[1]
        response = requests.get("https://www.canadapost.ca/trackweb/rs/track/json/package/"+trackingID+"/detail")
        jsonData = json.loads(response.text)
        status = jsonData['status']

        history = []
        for x in jsonData['events']:
            history.append([
                'Date: '+ x['datetime']['date'] + x['datetime']['time'] + x['datetime']['zoneOffset'],
                'Location: '+ x['locationAddr']['city'] + ", " + x['locationAddr']['regionCd'] + " (" + x['locationAddr']['countryCd'] + ")",
                'Description: '+ x['descEn']
            ])
        currentStatusData = history[0]
        currentStatusData = "\n".join(currentStatusData)
        del history[0]
        
        historyData = []
        for i in range(len(history)):
            historyData.append("\n".join(history[i]))
        
        historyData = "\n\n".join(historyData)

        context.bot.send_message(chat_id=update.effective_chat.id, text="*Shipping Status: *\n\n`Latest Status:\n"+currentStatusData+"`\n\n*Tracking Info:*\n\n`"+historyData+"`", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.MARKDOWN)

#Bot Start Message /start
@run_async
def start(update: Update, context: CallbackContext):
    context.bot.sendChatAction(update.effective_chat.id, "typing")
    cmd_msg = context.bot.send_message(chat_id=update.effective_chat.id, text="Hey there! I'm Shipping Info Bot!\nI can provide you latest tracking info on your package.\n\nUse the following commands to access your package tracking info.")

def main():
    
    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    #Command handler for E-Kart Logistics
    ekart_handler = CommandHandler("ekart", ekart)
    dispatcher.add_handler(ekart_handler)
    
    #Command handler for Pitney Bowes
    pitneyb_handler = CommandHandler("pitneyb", pitneyb)
    dispatcher.add_handler(pitneyb_handler)

    #Command handler for Canada Post
    canadapost_handler = CommandHandler("canadapost", canadapost)
    dispatcher.add_handler(canadapost_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":

    print(" _____ _     _             _            _____       __     ______       _   \n")
    print("/  ___| |   (_)           (_)          |_   _|     / _|    | ___ \     | |  \n")
    print("\ `--.| |__  _ _ __  _ __  _ _ __   __ _ | | _ __ | |_ ___ | |_/ / ___ | |_ \n")
    print(" `--. \ '_ \| | '_ \| '_ \| | '_ \ / _` || || '_ \|  _/ _ \| ___ \/ _ \| __|\n")
    print("/\__/ / | | | | |_) | |_) | | | | | (_| || || | | | || (_) | |_/ / (_) | |_ \n")
    print("\____/|_| |_|_| .__/| .__/|_|_| |_|\__, \___/_| |_|_| \___/\____/ \___/ \__|\n")
    print("              | |   | |             __/ |                                   \n")
    print("              |_|   |_|            |___/                                    ")

    main()
