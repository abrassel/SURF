from flask import Flask, request
import message_loader
from message_loader import TOKEN
import json as j


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

@app.route('/', methods=['POST'])
def index():
    if request.json:
        print(request.get_json())
        print(manager.group_list)
        print(request.json['group_id'])
    manager.send_message('this is a test response',request.json['group_id'])


if __name__ == '__main__':
    print('ran')
