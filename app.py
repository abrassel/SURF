from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    if request.json:
        print request.get_json()
    return "Hello World"


if __name__ == '__main__':
    app.run(debug=True)
