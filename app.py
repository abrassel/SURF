from flask import Flask, request
import interface
from interface import TOKEN, BOT_NAME
import json as j
from time import sleep

app = Flask(__name__)
manager = interface.Manager(TOKEN)

def post(bot, msg):
    if not manager.muted[bot.group_id]:
        bot.post(text=msg)

def parse(token):
    if token[0] != '!':
        return (None, None)
    
    tokens = token.split(' ')
    cmd = tokens[0][1:]
    if len(tokens) > 1:
        args = " ".join(tokens[1:])
    else:
        args = None

    return cmd.strip().lower(), args


@app.route('/', methods=['GET','POST'])
def webhook():
    print('started method')
    if not request.json:
        print('something fucked up')
        return '404'
    
    if request.json['sender_type'] == 'bot':
        print('avoid echoing')
        return '200'

    chat_id = request.json['group_id']
    if not chat_id:
        print('no chat id')
        return '200'
    
    sender_id = request.json['sender_id']
    cmd, args = parse(request.json['text'])
    
    try:
        bot = manager.bots[chat_id]
    except KeyError:
        print('key error, channel not found')
        print(chat_id)
        print(repr(manager.bots))
        return '200'
    

    if not cmd:
        return '200'

    help_str = '''
    valid commands
    -------------------------

    USER
    -------------------------
    - groups: list all groups
    - join <group>: join group
    - create <new_group>: create a new group
    - add_meme <text> <img attachment>: associate attached image with text
    - subscribe <usr>: subscribe a user to daily cat facts
    - report <usr>: report a user for malicious bot usage
    - unsubscribe: unsubscribe yourself from cat facts (25% chance of success)
    - help: view available commands (this dialogue)
    - opt-in: opt-in to announcements
    - opt-out: opt-out of announcements
    - announce: send group-wide announcement to all opted-in members
    

    ADMIN
    -------------------------
    - add <usr>: Add user to current group
    - mute/unmute: mute or unmute bot in a group
    - hook <channel name>: add bot to channel 
    - unhook: remove bot from channel
    - privilege <channel name> <admin/all>: restrict bot usage to admin/all
    '''

    # without arguments

    if manager.privileged[chat_id] and not manager.is_owner(sender_id, chat_id):
        print('failed privilege check')
        return '200'

    elif cmd == 'help':
        post(bot,help_str)
        
    elif cmd == 'groups':
        post(bot,'\n'.join(
            [group.name for group in manager.group_list.values()]
        ))
        print(manager.group_list)

    elif cmd == 'mute' and not manager.muted[chat_id]:
        post(bot,'muted')
        manager.muted[chat_id] = True


    elif cmd == 'unmute':
        manager.muted[chat_id] = False
        post(bot,'unmuted')

    elif cmd == 'unhook':
        try:
            manager.destroy(bot)
        except Exception:
            post(bot, 'Tried to unhook too quickly after creation')

    elif cmd == 'update':
        manager.update()

        
    #with arguments
    elif not args:
        return '200'

    elif cmd == 'privilege':
        if manager.is_owner(sender_id, chat_id):
            if args == 'admin':
                manager.privileged[chat_id] = True
                post(bot,'succesfully privileged channel')
            elif args == 'all':
                post(bot,'succesfully deprivileged channel')
                manager.privileged[chat_id] = False
        else:
            post(bot,'you are not the admin')    
    

    elif cmd == 'join':
        manager.join(chat_id, sender_id, args)

    elif cmd == 'create':
        manager.create_group(chat_id, sender_id, args)

    elif cmd == 'hook':
        manager.create_bot(args)

    elif cmd == 'add':
        name = args.lower()
        matches = []
        for usr in manager.nist.members:
            if name in usr.nickname.lower():
                matches.append(usr)

        if len(matches) == 1:
            matches[0].add_to_group(chat_id)
        elif len(matches) == 0:
            post(bot, "no matches for user \"%s\"" % (args,))
        else:
            post(bot, "Matches:\n------------\n" + "\n".join([usr.nickname for usr in matches]))
    '''
    
    if "groups" in request.json['text']:
        groups = ""
        for group in manager.group_list.values():
            groups += group.name + "\n"
        manager.msg_bot(groups)

    if "share" in request.json['text']:
        target = " ".join(request.json['text'].split(" ")[1:])
        for group in manager.group_list.values():
            if target.lower() == group.name.lower():
                manager.msg_bot("%s: %s" % (target,group.share_url))
                

    if "create" in request.json['text']:
        target = " ".join(request.json['text'].split(" ")[1:])
        group = manager.myself.groups.create(name=target,share=True)
        manager.group_list[group.id] = group
        for user in manager.bot_group.members:
            if user.user_id == sender_id:
                user.add_to_group(group.group_id)
                break
        sleep(3)
        group.change_owners(sender_id)
        #group.leave()
        manager.msg_bot("Created group %s at %s" % (target, group.share_url))

    if "join" in request.json['text']:
        target = " ".join(request.json['text'].split(" ")[1:])
        for group in manager.group_list.values():
            if group.name.lower() == target.lower():
                for user in manager.bot_group.members:
                    if user.user_id == sender_id:
                        user.add_to_group(group.group_id)
                        break
                break
    ''' # <- Legacy implementations
            
    return '200'

