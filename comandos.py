# c1 reference catalog
# c2 current catalog
# discount % of discount to show alert

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json, requests
import telegram.bot
from telegram.ext import messagequeue as mq
import math

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

def goo_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB5ZBe1AqH524qUDpons9lgV6WC-P1xXJU'
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    d = json.loads(r.text)
    return d['id']
    
    
class MQBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        super(MQBot, self).send_message(*args, **kwargs)


q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
testbot = MQBot("506432655:AAFGQ8BSRhVKxc1tg8dMBmFP8grjVpmae38", mqueue=q)
upd = telegram.ext.updater.Updater(bot=testbot)

def getDiscount(c1, c2, discount, chanelID): # chanel id: -284240927
    i = 0
    for x1 in list(c1.values()):
        if x1['id'] not in c2:
            i += 1
            continue
            
        x2 = c2[x1['id']]
        if x1['price']*(1-discount/100.0) > x2['price']:
        #if x1['price']*(1+discount/100.0) < x2['price']:
            actualDiscount = math.floor((x1['price'] - x2['price'])/x1['price']*100)
            marker = ''
            if actualDiscount > 30: marker = '⚪️'
            if actualDiscount > 40: marker = '⚫️'
            if actualDiscount > 60: marker = '🔵'
            if actualDiscount > 80: marker = '🔴'
            message = marker + " " + str(actualDiscount) + "%  " + str(x1['price']) + " => " + str(x2['price']) + "$  " + goo_url(x1['uri'])
            print(message)
            testbot.send_message(chat_id=chanelID, text=message, timeout=5000)
     
    print(str(i))
    
  
