import requests
import json
from time import time
import os

SEND_URL = '/direct_messages'
token = 'Tb4nzBPaxX9YXzw382Zm3g7jb0MFYPRzLAWl2FeIq'

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'X-Access-Token': os.environ.get('token'),
}

base = 'https://api.groupme.com/v3'

class API:
    def __init__(self):
        pass
    
    @staticmethod
    def send_msg(user_id, msg):
        data = {"direct_message":
        {
            "text": msg,
            "attachments": [],
            "recipient_id": user_id,
            "source_guid": str(time())}
        }

        data = json.dumps(data, indent=2)

        print(requests.post(base + SEND_URL,
                      headers=headers,
                      data=str(data)).__dict__)
