import requests
import json
from time import time

SEND_URL = '/direct_messages'
token = 'Tb4nzBPaxX9YXzw382Zm3g7jb0MFYPRzLAWl2FeIq'

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'X-Access-Token': 'Tb4nzBPaxX9YXzw382Zm3g7jb0MFYPRzLAWl2FeI',
}


class API:
    def __init__(self):
        self.base = 'https://api.groupme.com/v3'

    def send_msg(self, user_id, msg):
        data = {"direct_message":
        {
            "text": msg,
            "attachments": [],
            "recipient_id": user_id,
            "source_guid": str(time())}
        }

        data = json.dumps(data, indent=2)

        return requests.post(self.base + SEND_URL,
                      headers=headers,
                      data=str(data))
