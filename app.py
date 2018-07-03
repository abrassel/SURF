from flask import Flask, request
from API import API

valid_commands = set([
    'help', 'groups', 'join', 'create',
    'add', 'subscribe', 'unsubscribe', 'report', 'ban',
    'info', 'heritage', 'unban'
    ])
has_args = set([
    'join', 'create', 'add', 'subscribe',
    'report', 'ban'
    ])

admin = set([
    'heritage',
    'ban',
    'unban'
    ])

app = Flask(__name__)
api = API()

def parse(token):
    if token[0] != '!' or len(token) == 1:
        return (None, None)


    
    words = token[1:].split(' ') 

    cmd = words[0]

    arg = None
    if len(words) > 1:
        arg = " ".join(words[1:])


    return cmd, arg


def help(args, uid):
    help_str = '''
    Available Commands
    ------------------
    help: print this dialogue.
    add <usr> :: <group>: add a user to named group
    groups: list all groups.
    join <group>: self-explanatory.
    create <group>: create new group.
    add <usr> <group>: add user to this group.
    subscribe <usr>: subscribe user to Cat Facts.
    unsubscribe: unsubscribe yourself from Cat Facts.
    -------
    report <usr>: report user for misuse of bot
    ban <usr>: (ADMIN ONLY) ban user from bot
    '''
    api.send_msg(uid,help_str)
    

def groups(args, uid):
    result = '\n'.join(api.groups)

    api.send_msg(uid, result)

def join(args, uid):

    if args not in api.groups:
        api.send_msg(uid, 'This group is not visible or does not exist.')
        return
    
    api.add_member(api.groups[args], uid)

def create(args, uid):
    share = api.create_group(args, uid)
    response = 'Created group %s at %s' % (args,share)

    print('Response: ' + response)

    api.send_msg(uid,response)
        
    

def add(args, uid):
    args = args.split('::')

    if len(args) != 2:
        api.send_msg(uid, '!add <usr> :: <group>')
        return
    usr,group = [arg.strip() for arg in args]

    if group not in api.groups or (
            usr not in api.people):
        api.send_msg(uid, 'Group or user does not exist.')
        return

    api.add_member(api.groups[group], api.people[usr])
    

def subscribe(args, uid):
    result = api.subscribe(args)
    if result == -1:
        api.send_msg(uid, 'User %s is already subscribed.' % (args,))
    elif result == -2:
        api.send_msg(uid, 'User %s does not exist.' % (args,))
    else:
        api.send_msg(uid, 'Successfully subscribed user % s.' % (args,))
        api.send_msg(int(api.people[args]),
                     'You have been subscribed to cat facts by %s!  Enjoy!'
                     % (api.name(str(uid)),))

def unsubscribe(args, uid):
    result = api.unsubscribe(str(uid))

    if result == -1:
        api.send_msg(uid, 'You are not currently subscribed to cat facts.')

    elif result == -2:
        api.send_msg(uid, 'Your RNG was not high enough.  Unsubscribing only has a 25% chance of success.')

    else:
        api.send_msg(uid, 'Successfully unsubscribed!')

def heritage(args, uid):
    api.send_msg(uid, 'Updating!')
    api.heritage(0)
    api.send_msg(uid, str(api.groups))
    api.send_msg(uid, str(api.people))

def info(args, uid):
    api.send_msg(uid, 'Current state: ')
    api.send_msg(uid, str(api.groups))
    api.send_msg(uid, str(api.people))
    
def report(args, uid):
    api.send_msg(api.people['Brassel Sprouts'],
                 'User %s has reported %s' % (api.name(uid),
                                              args))
                                              

def ban(args, uid):
    api.ban(args)


def unban(args, uid):
    api.unban(args)



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

    if cmd in admin and user_id != self.people['Brassel Sprouts']:
        print('Tried to access admin command')
        return '400'

    if cmd in has_args and not args:
        print('missing args')
        return '400'

    eval(cmd+'("'+str(args)+'",'+user_id+')')
    
    

    
    
    return '200'
