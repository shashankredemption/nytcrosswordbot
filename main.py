import os
from time import mktime
from datetime import datetime, timedelta
from pytz import timezone
from models import User
from fbchat import Client
from fbchat.models import Message, ThreadType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

client = Client(os.environ['USERNAME'], os.environ['PASSWORD'])
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

def add_new_users(users):
    for user in users:
        try:
            session.query(User).filter(User.name == user.name).one()
        except:
            session.add(User(id=user.uid, name=user.name, win_count=0, loss_count=0, dnf_count=0, stupid_alex_count=0))
            session.commit()

def parse_message(message):
    try:
        if 'dnf' in message.lower().split()[0]:
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

def handle_stupid_alex(dictionary):
    alex_dict = {v: k for k, v in dictionary.items() if v.lower().startswith('alex')}
    if len(alex_dict) != 2:
        return ''
    stupid_alex = max(alex_dict, key=alex_dict.get)
    stupid_alex_row = session.query(User).filter(User.name == stupid_alex).one()
    stupid_alex_row.stupid_alex_count += 1
    return f'Today\'s stupid_alex Alex is {stupid_alex}. They have been Stupid Alex {stupid_alex_row.stupid_alex_count} times.'

# def handle_tony(dictionary):
#     return 'Anthony Ma' in dictionary[min(list(dictionary.keys()))]

def handle_winners(dictionary):
    output = ''
    for winner in [dictionary[min(list(dictionary.keys()))]]:
        winner_row = session.query(User).filter(User.name == winner).one()
        winner_row.win_count += 1
        output += f'{winner_row.name} now has {winner_row.win_count} wins\n'
    return output

def handle_losers(dictionary):
    output = ''
    for loser in [dictionary[max(list(dictionary.keys()))]]:
        loser_row = session.query(User).filter(User.name == loser).one()
        loser_row.loss_count += 1
        output += f'{loser_row.name} now has {loser_row.loss_count} losses\n'
    return output

def handle_dnf(dictionary):
    output = ''
    dnf_dict = [v for k, v in dictionary.items() if k == float('inf')]
    for dnfer in dnf_dict:
        dnfer_row = session.query(User).filter(User.name == dnfer).one()
        dnfer_row.dnf_count += 1
        output += f'{dnfer_row.name} now has {dnfer_row.dnf_count} dnfs\n'
    return output

def build_output(dictionary):
    output = 'Scoreboard: \n'
    count = 1
    sorted_times = sorted(dictionary.items(), key=lambda item: item[0])
    for k, v in sorted_times:
        output += f'{count}. {v} @ {format_time(k)} \n'
        count += 1
    output += '\n'
    output += handle_winners(dictionary)
    output += handle_losers(dictionary)
    output += handle_dnf(dictionary)
    output += handle_stupid_alex(dictionary)
    # output += f'Did Tony Ma Win? {"Yes :(" if handle_tony(dictionary) else "NO! :D"} \n'
    session.commit()
    return output

messages = client.fetchThreadMessages(os.environ['THREAD_ID'], limit=200)
messages.reverse()
day = datetime.now(tz=timezone('US/Eastern')) - timedelta(days=1)
weekday = day.weekday()
if weekday == 5 or weekday == 6:
    release_time = day.replace(hour=18, minute=0, second=0).timetuple()
else:
    release_time = day.replace(hour=22, minute=0, second=0).timetuple()
release_time = mktime(release_time)
messages = filter(lambda x: int(x.timestamp[:10]) > release_time, messages)
time_dict = {}
for message in messages:
    time = parse_message(message.text)
    if time:
        time_dict[message.author] = time
user_dict = {}
users = list(client.fetchUserInfo(*list(time_dict.keys())).values())
add_new_users(users)
for user in users:
    user_dict[time_dict[user.uid]] = user.name
client.send(Message(text=build_output(user_dict)), thread_id=os.environ['SEND_THREAD_ID'], thread_type=ThreadType.GROUP)
