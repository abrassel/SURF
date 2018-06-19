import requests

class API:
    def __init__(self, token):
        self._base = "https://api.groupme.com/v3"
        self._headers = {"Content-Type": "applications/json"}
        self._params = {"token": token}


    def send_msg(self, user_id, msg):
        data = {'source_guid': 'GUID',
                'recipient_id': user_id,
                'text': msg
                }

        self.__post__(extension="/direct_messages",data=data)
        

    def __post__(self,extension,data):
        r = requests.post(self._base + extension, headers=self._headers,
                             params=self._params, data=data).json()
        print(r.__dict__)
        return r
