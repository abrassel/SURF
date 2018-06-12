from flask import Flask, request
import message_loader
from message_loader import TOKEN
import json as j


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

@app.route('/', methods=['POST'])
def index():
    if request.json and request.json['sender_type'] != 'bot':

        if "groups" in request.json['text']:
            groups = ""
            for group in manager.myself.groups.list_all():
                groups += group.name + "\n"

            ind = 0
            for ind in range(0,len(groups),100):
                manager.msg_bot(groups[ind:ind+100])
            if ind < len(groups):
                manager.msg_bot(groups[ind:])
    return '200'


if __name__ == '__main__':
    print('ran')
