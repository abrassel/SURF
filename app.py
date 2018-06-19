from flask import Flask, request
import os
from API import API

valid_commands = set([
    'help', 'groups', 'join', 'create',
    'add', 'subscribe', 'unsubscribe', 'report', 'ban'
    ])
has_args = set([
    'join', 'create', 'add', 'subscribe',
    'report', 'ban'
    ])

app = Flask(__name__)
api = API(os.environ.get('token'))

def parse(token):
    if token[0] != '!' or len(token) == 1:
        return (None, None)


    
    words = token[1:].split(' ') 

    cmd = words[0]

    arg = None
    if len(words) > 1:
        arg = " ".join(words[1])


    return cmd, arg


def help(args, uid):
    help_str = '''
    Available Commands
    ------------------
    help: print this dialogue.
    groups: list all groups.
    join <group>: self-explanatory.
    create <group> [share_group]: create group, optionally share to share_group.
    add <usr> <group>: add user to this group.
    subscribe <usr>: subscribe user to Cat Facts.
    unsubscribe: unsubscribe yourself from Cat Facts.
    -------
    report <usr>: report user for misuse of bot
    ban <usr>: (ADMIN ONLY) ban user from bot
    '''
    api.send_msg(uid,help_str)
    

def groups(args, uid):
    pass

def join(args, uid):
    pass

def create(args, uid):
    pass

def add(args, uid):
    pass

def subscribe(args, uid):
    pass

def unsubscribe(args, uid):
    pass



@app.route('/', methods=['POST'])
def webhook():

    print('started method')

    if not request.json:
        print('there was no json')
        return '400'

    print(request.get_json())

    try:
        user_id = request.json['user_id']
        text = request.json['text']
    except KeyError:
        print('key error')
        return '400'
        
    if len(request.json['group_id']) < 10:
        print('this is a group message')
        return '200'


    # non args commands

    cmd, args = parse(text)

    if not cmd:
        print('missing cmd')
        return '400'

    if cmd not in valid_commands:
        print('invalid command')
        return '400'

    if cmd in has_args and not args:
        print('missing args')
        return '400'

    eval(cmd+'('+str(args)+','+user_id+')')
    
    

    
    
    return '200'
