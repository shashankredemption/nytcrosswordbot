import os
import json
import random
import sys
from time import mktime
from datetime import datetime, timedelta
from pytz import timezone
from models import User
from fbchat import Client
from fbchat.models import Message, ThreadType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

client = Client(os.environ['NYT_USER'], os.environ['NYT_PASS'], session_cookies=cookies)
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()
now = datetime.now(tz=timezone('US/Eastern'))

def add_new_users(users):
    for user in users:
        try:
            session.query(User).filter(User.name == user.name).one()
        except:
            session.add(User(id=user.uid, name=user.name, win_count=0, loss_count=0, dnf_count=0, stupid_alex_count=0, lame_count=0))
            session.commit()

def parse_message(message):
    try:
        if 'dnf' in message.lower().split()[0]:
            return float('inf')
        message = message.replace(":", "").replace("*", "")
        return int(message.split()[0])
    except (ValueError, AttributeError, IndexError) as e:
        return False

def format_time(time):
    timestr = str(time)
    if time == float('inf'):
        return 'dnf'
    elif len(timestr) == 1:
        return f'0:0{timestr}'
    elif len(timestr) > 2:
        return f'{timestr[:-2]}:{timestr[-2:]}'
    else:
        return f'0:{timestr}'

def handle_stupid_alex(dictionary):
    alex_dict = {k: v for k, v in list(dictionary.items())[::-1] if k.lower().startswith('alex')}
    if len(alex_dict) != 2:
        return ''
    stupid_alex = max(alex_dict, key=alex_dict.get)
    stupid_alex_row = session.query(User).filter(User.name == stupid_alex).one()
    stupid_alex_row.stupid_alex_count += 1
    return f'Today\'s Stupid Alex is {stupid_alex}\n'

def handle_arcadia(dictionary):
    apaches = ['Anthony Ma', 'Katelyn Yu']
    apache_dict = {k: v for k, v in list(dictionary.items()) if k in apaches}
    if len(apache_dict) != 2:
        return ''
    top_apache = min(apache_dict, key=apache_dict.get)
    top_apache_row = session.query(User).filter(User.name == top_apache).one()
    top_apache_row.top_apache_count += 1
    return f'Today\'s Top Arcadian is {top_apache}\n'

# def handle_tony(dictionary):
#     return 'Anthony Ma' in dictionary[min(list(dictionary.keys()))]

def handle_winners(dictionary):
    output = ''
    for winner in dictionary[min(list(dictionary.keys()))]:
        winner_row = session.query(User).filter(User.name == winner).one()
        winner_row.win_count += 1
        output += f'{winner_row.name} now has {winner_row.win_count} wins\n'
    return output

def handle_losers(dictionary):
    output = ''
    for loser in dictionary[max(list(dictionary.keys()))]:
        loser_row = session.query(User).filter(User.name == loser).one()
        loser_row.loss_count += 1
        output += f'{loser_row.name} now has {loser_row.loss_count} losses\n'
    return output

def handle_dnf(dictionary):
    output = ''
    dnf_dict = dictionary.get(float('inf'), [])
    for dnfer in dnf_dict:
        dnfer_row = session.query(User).filter(User.name == dnfer).one()
        dnfer_row.dnf_count += 1
        output += f'{dnfer_row.name} now has {dnfer_row.dnf_count} dnfs\n'
    return output

LAME_THRESHOLD = 10
def handle_lames(name_to_time, members):
    # pull up all users
    # lames are users that are in set of all users
    # but not in (input) dictionary
    participants = name_to_time.keys()
    lames = []
    output = ''
    for user in session.query(User).all():
        # if they particpated, reset their lame count
        # otherwise, add 1 lame
        if user.name in participants or user.lame_count == None:
            user.lame_count = 0
        else:
            user.lame_count += 1
            # check if they've reached the lame threshold
            # add them to the output if so
            if user.name in members:
                if user.lame_count > LAME_THRESHOLD:
                    lames.append(user.name)
                elif user.lame_count > (LAME_THRESHOLD - 3):
                    output += f'{user.name} has {LAME_THRESHOLD - user.lame_count} days til 🦵\n'
    if lames:
        output += f"Prepare 4 🦵: {', '.join(lames)}\n"
    return output

def build_output(uid_to_time, participants, members):
    time_to_names = {}
    name_to_time = {}
    for participant in participants:
        if uid_to_time[participant.uid] in time_to_names:
            time_to_names[uid_to_time[participant.uid]].append(participant.name)
        else:
            time_to_names[uid_to_time[participant.uid]] = [participant.name]
        name_to_time[participant.name] = uid_to_time[participant.uid]

    output = f'Scoreboard for {now.strftime("%A %m/%d")}: \n'
    count = 1
    sorted_times = sorted(time_to_names.items(), key=lambda item: item[0])
    for key, values in sorted_times:
        for name in values:
            output += f'{count}. {name} @ {format_time(key)} \n'
        count += len(values)
    output += '\n'
    output += handle_winners(time_to_names)
    handle_losers(time_to_names)
    handle_dnf(time_to_names)
    output += handle_stupid_alex(name_to_time)
    output += handle_arcadia(name_to_time)
    # output += f'Did Tony Ma Win? {"Yes :(" if handle_tony(dictionary) else "NO! :D"} \n'
    output += handle_lames(name_to_time, members)
    return output

def get_times():
    day = now - timedelta(days=1)
    weekday = day.weekday()
    if weekday == 5 or weekday == 6:
        release_time = day.replace(hour=18, minute=0, second=0).timetuple()
    else:
        release_time = day.replace(hour=22, minute=0, second=0).timetuple()
    if now.weekday() == 5 or now.weekday() == 6:
        end_time = now.replace(hour=18, minute=0, second=0).timetuple()
    else:
        end_time = now.replace(hour=22, minute=0, second=0).timetuple()
    release_time = mktime(release_time)
    end_time = mktime(end_time)

    return release_time, end_time

def main():
    messages = client.fetchThreadMessages(os.environ['THREAD_ID'], limit=200)
    messages.reverse()
    thread = client.fetchThreadInfo(os.environ['THREAD_ID'])[os.environ['THREAD_ID']]
    members = [member.name for member in client.fetchAllUsersFromThreads([thread])]

    # get times and filter
    release_time, end_time = get_times()
    messages = filter(lambda x: int(x.timestamp[:10]) > release_time and int(x.timestamp[:10]) < end_time, messages)
    uid_to_time = {}
    for message in messages:
        parsed_time = parse_message(message.text)
        if parsed_time:
            uid_to_time[message.author] = parsed_time
    participants = list(client.fetchUserInfo(*list(uid_to_time.keys())).values())
    add_new_users(participants)
    output = build_output(uid_to_time, participants, members)
    print(output)
    if '--send' in sys.argv:
        client.send(Message(text=output), thread_id=os.environ['SEND_THREAD_ID'], thread_type=ThreadType.GROUP)
    if '--commit' in sys.argv:
        session.commit()

main()
