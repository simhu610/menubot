# This Python file uses the following encoding: utf-8
import os
import sys
import time
from slackclient import SlackClient
import readmenu
import datetime
import cPickle

import skipgram
import cbow
import random

BOT_ID = "U561US9MJ"

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

vectorizer_svc = cPickle.load(open("vectorizer_svc2.txt", 'rb'))
vectorizer = vectorizer_svc['vectorizer']
svc = vectorizer_svc['svc']


def get_restaurant(command):
    BRA_MAT = 0
    HOMEMADE = 1
    restaurant = BRA_MAT
    restaurant_keywords = {BRA_MAT: ["bra mat", "bramat"],
                           HOMEMADE: ["home made", "homemade", "home maid", "homemaid"]}
    for restaurant_key in restaurant_keywords:
        for keyword in restaurant_keywords[restaurant_key]:
            if keyword in command:
                restaurant = restaurant_key
    return restaurant


def get_response(command, restaurant=None):

    response = "Which day do you want the menu for? (today, i morgon, måndag, Wednesday, ...)"

    if restaurant is None:
        restaurant = get_restaurant(command)

    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    swe_to_eng = {u'måndag': 'monday', u'tisdag': 'tuesday', u'onsdag': 'wednesday', u'torsdag': 'thursday', u'fredag': 'friday'}
    today_keywords = ['today', 'idag', 'i dag', 'nu', 'now']
    tomorrow_keywords = ['tomorrow', 'imorgon', 'i morgon']

    day = None

    if command in weekdays:
        day = command
    elif command in swe_to_eng.keys():
        day = swe_to_eng[command]
    elif command in today_keywords:
        weekday_index = datetime.datetime.today().weekday()
        if weekday_index >= 0 and weekday_index < len(weekdays):
            day = weekdays[weekday_index]
        else:
            response = "There is no food {}".format(command)
    elif command in tomorrow_keywords:
        weekday_index = datetime.datetime.today().weekday() + 1
        if weekday_index >= 0 and weekday_index < len(weekdays):
            day = weekdays[weekday_index]
        else:
            response = "There is no food {}".format(command)
    else:
        all_keywords = weekdays + swe_to_eng.keys() + today_keywords + tomorrow_keywords
        for word in command.split():
            for keyword in all_keywords:
                if keyword in word:
                    return get_response(keyword, restaurant)

    if day:
        response = readmenu.get_menu(day, restaurant)

    return response

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    response = get_response(command)

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def score(w1, w2):
    if len(w1) == 0:
        return len(w2)
    if len(w2) == 0:
        return len(w1)
    if w1[-1] == w2[-1]:
        cost = 0
    else:
        cost = 1
    return min(score(w1[:-1], w2) + 1,
               score(w1, w2[:-1]) + 1,
               score(w1[:-1], w2[:-1]) + cost)


def react(output):
    # emojis = ["apple", "lemon", "tomato", "hot_pepper", "corn", "sweet_potato", "cheese_wedge", "meat_on_bone",
    #           "fried_shrimp", "egg", "hamburger", "fries", "hotdog", "pizza", "spaghetti", "taco"]
    emojis = ["apple", "lemon", "tomato", "corn", "egg", "hamburger", "fries", "hotdog", "pizza", "spaghetti", "taco"]
    for word in output['text'].lower().split():
        if len(word) > max([len(e) for e in emojis]) + 3:
            continue
        for emoji in emojis:
            # if score(word, emoji) <= 2:
            old_score = score(word, emoji)
            new_score = 2.0 * old_score / (len(word) + len(emoji))
            if new_score < 0.4:
                slack_client.api_call("reactions.add", channel=output['channel'], name=emoji, timestamp=output['ts'])


def react2(output):
    emoji = svc.predict(vectorizer.transform([output['text']]))[0]
    if emoji != "NO_REACTION":
        slack_client.api_call("reactions.add", channel=output['channel'], name=emoji, timestamp=output['ts'])


def change_sentence(output):
    if output['user'] != BOT_ID:
        response = None
        new_sentence, num_replaced_words = skipgram.replace_words(output['text'])
        if num_replaced_words >= 2 and random.randint(1, 10) == 6:
            response = "Or as I would put it: `{}`".format(new_sentence)
        else:
            new_sentence, num_replaced_words = cbow.replace_words(output['text'])
            if num_replaced_words >= 1 and random.randint(1, 10) == 6:
                response = "Did you mean `{}` ?".format(new_sentence)
        if response is not None:
            slack_client.api_call("chat.postMessage", channel=output['channel'], text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
            if output and 'text' in output:
                react(output)
                react2(output)
                change_sentence(output)
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("MenuBot connected and running!")
        while True:
            try:
                slack_rtm_output = slack_client.rtm_read()
            except:
                print "Connection closed? Trying to reconnect..."
                if slack_client.rtm_connect():
                    print("MenuBot connected and running, again!")
                    continue
                else:
                    print("Connection failed. Invalid Slack token or bot ID?")
                    break
            try:
                command, channel = parse_slack_output(slack_rtm_output)
            except:
                print "Unexpected error in parse_slack_output:", sys.exc_info()[0]
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
