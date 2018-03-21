# This Python file uses the following encoding: utf-8
import os
from slackclient import SlackClient
import cPickle

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

history = slack_client.api_call("channels.history", channel='C3W65FLP4')
messages = history['messages']
# has_more = history['has_more']
# ok = history['ok']
# print len(messages)
#
# while has_more and ok:
#     oldest_message_already_fetched = messages[-1]['ts']
#
#     history = slack_client.api_call("channels.history", channel='C3W65FLP4', latest=oldest_message_already_fetched, inclusive=False)
#     messages = messages + history['messages']
#     has_more = history['has_more']
#     ok = history['ok']
#     print len(messages)

cPickle.dump(messages, open("messages_C3W65FLP4_dummy.txt", 'wb'))
