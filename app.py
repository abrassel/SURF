from flask import Flask, request
import message_loader
from message_loader import TOKEN
import json as j


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

@app.route('/', methods=['POST'])
def index():
    if request.json and request.json['name'] != 'Brassel Sprouts':
        manager.send_message('this is a test response',request.json['group_id'])


if __name__ == '__main__':
    print('ran')
