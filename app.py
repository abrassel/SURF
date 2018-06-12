from flask import Flask, request
import message_loader
from message_loader import TOKEN, NIST_ID, BOT_NAME
import json as j
from time import sleep


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

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
    if not request.json:
        # something fucked up
        return '404'
    
    if request.json['sender_type'] == 'bot':
        # avoid echoing
        return '200'

    
    chat_id = request.args.get('chat',default=NIST_ID,type=str)
    sender_id = request.json['sender_id']
    cmd, args = parse(request.json['text'])

    if not cmd:
        return '200'

    help_str = '''
    valid commands
    -------------------------
    - groups: list all groups
    - join <group>: join group
    - create <new_group>: create a new group
    - mute/unmute: admin can mute or unmute bot in a group
    - add_meme <meme> <tag>: post an image macro in response to a text key phrase (vote majority)
    - subscribe <usr>: subscribe a user to daily cat facts
    - report <usr>: report a user for malicious bot usage
    - unsubscribe: unsubscribe yourself from cat facts (25% chance of success)
    - help: view available commands (this dialogue)
    '''

    if cmd == 'help':
        #manager.send_pm(sender_id, help_str)
        manager.msg_bot(help_str)
        
    if cmd == 'groups':
        manager.msg_bot('\n'.join(
            [group.name for group in manager.group_list.values()]
        ))

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

