import os, slackclient, time
import requests
import random
import pandas as pd
from util import microstrategyfunctions

# delay in seconds before checking for new events 
SocketDelay = 1
# Slack Variables
SlackToken = ''
bot_name = ['dapi','dapy']


Slack = slackclient.SlackClient(SlackToken)
bot_ID = Slack.api_call('auth.test')['user_id']
bot_mention = '<@'+bot_ID+'>'
print('Bot ID is: '+bot_ID)



def post_message(message, channel, thread):
    if thread == None:
        Slack.api_call('chat.postMessage', channel=channel, text=message, as_user=True)
    else:
        Slack.api_call('chat.postMessage', channel=channel, text=message, as_user=True, thread_ts=thread)

greetings_words = ["hello", "hi", "greetings", "sup", "what's up", "hola", "hey"]
bye_words = ['bye', 'goodbye', 'revoir', 'adios', 'later', 'cya', 'chao', 'hasta luego', 'till later', "regards"]
showdata_phrases = ["Here's your answer: ", "Here you go: ", "Sure: ", "Here it is: ", "The data you asked for: "]
nodata_phrases = ["Sorry, I don't understand your question ", "Sorry, I can't handle your question", "I don't have an answer for your question", "I don't understand what you are saying"]
thankful_words = ["thanks" , "cool", "gracias", "great", "thank you", "thank"]
thankful_response = ["np" , "no problem", "glad to help", "you are welcome"]

def parse_greeting(token):
    for word in token:
        if word in greetings_words:
            return random.choice(greetings_words)
        if word in bye_words:
            return random.choice(bye_words)
    return ""

def parse_thanks(token):
    for word in token:
        if word in thankful_words:
            return random.choice(thankful_response)
    return ""

def handle_microstrategy_message (message, microstrategy_metrics, microstrategy_atributos, microstrategy_table, channel, thread):
    answer, graph_filename = microstrategyfunctions.get_answer_microstrategy(message, microstrategy_metrics, microstrategy_atributos, microstrategy_table)
    if len(answer) != 0:
        post_message (message = random.choice(showdata_phrases) , channel = channel, thread = thread)
        post_message (message = answer, channel = channel, thread = thread)
        if len(graph_filename) != 0:
            print (graph_filename)
            filegraph = open(graph_filename, 'rb')
            graph_id = Slack.api_call('files.upload', channels = channel, file = filegraph, initial_comment = 'Here is the graph', thread_ts = thread)['file']['id']
            filegraph.close()
            f = open("images_uploaded.txt", "a+")
            f.write('%s \n' % (graph_id))
            f.close()
        return True
    else:
        return False


def parse_message(event, microstrategy_metrics, microstrategy_atributos, microstrategy_table):
    message=event.get('text')
    thread=event.get('thread_ts')
    print (thread)
    token=[word.lower() for word in message.strip().split()]
    if bot_related(channel = event.get('channel'),token = token, user = event.get('user')):
        print ('Message for bot')
        if len(parse_greeting(token)) != 0: 
            post_message (message = parse_greeting(token), channel = event.get('channel'), thread = thread)
            handle_microstrategy_message (message = message, microstrategy_metrics = microstrategy_metrics, microstrategy_atributos = microstrategy_atributos, microstrategy_table = microstrategy_table, channel = event.get('channel'), thread = thread)
            return True
        else:
            if  len(parse_thanks(token)) != 0: 
                post_message(message = parse_thanks(token), channel = event.get('channel'), thread = thread)
                return True
            elif not handle_microstrategy_message (message = message, microstrategy_metrics = microstrategy_metrics, microstrategy_atributos = microstrategy_atributos, microstrategy_table = microstrategy_table, channel = event.get('channel'), thread = thread):
                post_message(message = random.choice(nodata_phrases), channel = event.get('channel'), thread = thread)
                return True
    else:
        print ('Message not for bot')
    return True


def bot_related(channel, token, user):
    channel_info = Slack.api_call('conversations.info',channel=channel)['channel']
    if 'user' not in channel_info:
        if bot_mention.lower() in token:
            return True
        for name in bot_name:
            if name in token:
                return True
        return False
    else:
        if bot_ID == user :
            return False
    return True

if __name__=='__main__':
    print ('Get MicroStrategy data')
    list_metrics,list_atributos,table = microstrategyfunctions.get_data_microstrategy()
    if Slack.rtm_connect():
        print('Receiving Slack events')
        while True: #True:
            event_list = Slack.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    if event['type'] != 'desktop_notification' and event['type'] != 'user_change':
                        print(event)
                    if event['type'] == 'message' and not 'subtype' in event:
                        parse_message(event,list_metrics,list_atributos,table)
            time.sleep(SocketDelay)
        
    else:
        print('Connection failed')