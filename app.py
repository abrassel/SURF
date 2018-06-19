from flask import Flask, request



app = Flask(__name__)


def parse(token):
    if token[0] != '!' or len(token) == 1:
        return (None, None)


    
    words = token[1:].split(' ') 

    cmd = words[0]

    arg = None
    if len(words) > 1:
        arg = " ".join(words[1])


    return cmd, arg


@app.route('/', methods=['POST'])
def webhook():

    print('started method')

    if not request.json:
        print('there was no json')
        return '400'

    print(request.get_json())
    
