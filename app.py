from flask import Flask, request
import message_loader
from message_loader import TOKEN
import json as j


app = Flask(__name__)
manager = message_loader.Manager(TOKEN)

@app.route('/', methods=['POST'])
def index():
    if request.json and request.json['name'] != 'testbot':
        manager.msg_bot('this is a test response')


if __name__ == '__main__':
    print('ran')
