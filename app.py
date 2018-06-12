from flask import Flask, request
import message_loader
from message_loader import TOKEN
import json as j


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

@app.route('/', methods=['POST'])
def index():
    if request.json and request.json['sender_type'] != 'bot':

        if "groups" in request.json.text:
            groups = ""
            for group in manager.group_list.list_all():
                groups += group.name + "\n"
            manager.msg_bot(groups)

    return '200'


if __name__ == '__main__':
    print('ran')
