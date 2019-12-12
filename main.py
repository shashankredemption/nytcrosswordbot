import os
from fbchat import Client
from fbchat.models import *
client = Client(os.environ['USERNAME'], os.environ['PASSWORD'])

def parse_message(message):
    try:
        if 'dnf' in message.lower().split():
            return float('inf')
        message = message.replace(":", "")
        return int(message)
    except (ValueError, AttributeError) as e:
        return False

def format_time(time):
    timestr = str(time)
    if time == float('inf'):
        return 'dnf'
    elif len(timestr) > 2:
        return f'{timestr[:-2]}:{timestr[-2:]}'
    else:
        return f'0:{timestr}'

def idiot_alex(dictionary):
    alex_dict = {k: v for k, v in dictionary.items() if k.lower().startswith('alex')}
    return max(alex_dict, key=alex_dict.get)

def did_tony_win(dictionary):
    return 'Anthony Ma' in dictionary[min(list(dictionary.keys()))]

def build_output(dictionary):
    output = 'Scoreboard: \n'
    count = 1
    sorted_times = sorted(dictionary.items(), key=lambda item: item[1])
    for k, v in sorted_times:
        output += f'{count}. {k} @ {format_time(v)} \n'
        count += 1
    output += '\n'
    output += f'Idiot Alex: {idiot_alex(dictionary)} \n'
    output += f'Did Tony Ma Win? {"Yes :(" if did_tony_win(dictionary) else "NO! :D"} \n'
    return output

messages = client.fetchThreadMessages(os.environ['THREAD_ID'], limit=150)
messages.reverse()
time_dict = {}
for message in messages:
    time = parse_message(message.text)
    if time:
        time_dict[message.author] = time
user_dict = {}
users = list(client.fetchUserInfo(*list(time_dict.keys())).values())
for user in users:
    user_dict[user.name] = time_dict[user.uid]
client.send(Message(text=build_output(user_dict)), thread_id=os.environ['SEND_THREAD_ID'], thread_type=ThreadType.GROUP)
