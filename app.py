from flask import Flask, request
import message_loader
from message_loader import TOKEN
import json as j


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

@app.route('/', methods=['GET','POST'])
def webhook():
    if not request.json:
        return '404'
    
    if request.json['sender_type'] == 'bot':
        return '200'

    
    chat_id = request.args.get('chat',default=NIST_ID,type=str)
    sender_id = request.json['sender_id']

    
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
        for user in manager.bot_group:
            if user.user_id == sender_id:
                user.add_to_group(group.group_id)
                break
        result = manager.myself.groups.change_owners(group.id, sender_id)
        #group.leave()
        manager.msg_bot("Created group %s at %s" % (target, group.share_url))
            
    return '200'


if __name__ == '__main__':
    print('ran')
