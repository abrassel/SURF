from flask import Flask, request
import message_loader
from message_loader import TOKEN
import json as j


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

@app.route('/', methods=['POST'])
def index():
    if not request.json:
        return '404'
    
    if request.json['sender_type'] == 'bot':
        return '200'

    if "groups" in request.json['text']:
        groups = ""
        for group in manager.group_list.values():
            groups += group.name + "\n"
        manager.msg_bot(groups)

    if "join" in request.json['text']:
        target = " ".join(request.json['text'].split(" ")[1:])
        for group in manager.group_list.values():
            if target.lower() == group.name.lower():
                manager.msg_bot("%s: %s" % (target,group.share_url))
                

    if "create" in request.json['text']:
        target = " ".join(request.json['text'].split(" ")[1:])
        group = manager.myself.groups.create(name=target,share=True)
        manager.group_list[group.id] = group
        manager.msg_bot("Created group % at %" % (target, group.share_url))
            
    return '200'


if __name__ == '__main__':
    print('ran')
