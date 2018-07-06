import requests
import json
from time import time, sleep
import os
from random import random
from threading import Thread
import pickle
import re

link = re.compile('https://\S*.?groupme.com/join_group/(\d+)/(\S+)')
HOME = 'Bot Testing Channel'
REPOSITORY = 'Bot Testing Channel'

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'X-Access-Token': os.environ.get('token'),
}

base = 'https://api.groupme.com/v3'

class API:
    def __init__(self):
        self.people = {}
        self.groups = {}
        self.bot_testing_channel = None

            
        self.t_heritage   = Thread(target=self.heritage,   args=(25*60,)).start()
        self.t_cat_facts  = Thread(target=self.cat_facts,  args=(25*60,)).start()


    def msg_bot_testing(self, msg):
        url = base + '/groups/'+self.bot_testing_channel+'/messages'

        data = {'source_guid': str(time()),
                'text': msg,
                'attachments': []
                }

        print(requests.post(url,headers=headers,data=json.dumps(data)).__dict__)
        
    
        
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

        requests.post(base + '/direct_messages',
                      headers=headers,
                      data=str(data))


    def create_group(self, name, uid):
            

        data = {'name':name,
                'share': True}

        reply = requests.post(base + '/groups',
                              headers=headers,
                              data=json.dumps(data)).json()
        self.groups[name] = reply['response']['group_id']

        data = {'requests':
                [{'group_id': self.groups[name], 'owner_id': str(uid)}]}

        sleep(1)

        results = self.add_member(self.groups[name],
                                  uid)
        if results == -1:
            return -1
                        
                                  
        sleep(1)
        requests.post(base + '/groups/change_owners',
                      headers=headers,
                      data=json.dumps(data))

        return reply['response']['share_url']

    def get_share_id(self, group_name):
        if group_name not in self.groups:
            return -2

        group_id = self.groups[group_name]
        url = base + '/groups/' + str(group_id)

        response = requests.get(url, headers=headers)

        return response.json()['response']['share_url']

    def add_member(self, group, user):
        
        
        url = base + '/groups/' + group + '/members/add'
        data = {'language': 'en-US',
                'members': [{
                    'nickname': self.name(str(user)),
                    'guid': str(time()),
                    'user_id': user
                }]
        }

        temp = requests.post(url,
                             headers=headers,
                             data=json.dumps(data)
        )

        
        
    @staticmethod
    def list_members(group):
        results = requests.get(base + '/groups/'+self.groups[group]).json()


    def subscribe(self, new_user):
        with open('subscribers.txt','rb') as subscribers:
            s = pickle.load(subscribers)
        if new_user not in self.people:
            if new_user not in self.people:
                return -2

        
        user_id = self.people[new_user]
        if user_id in s:
            return -1


        s.add(user_id)
        print('This is the result: ' + str(s))
        with open('subscribers.txt','wb') as subscribers:
            pickle.dump(s, subscribers)
        
    def unsubscribe(self, cur_user):
        with open('subscribers.txt','rb') as subscribers:
            s = pickle.load(subscribers)
        
        if cur_user not in s:
            return -1

        if random() > .9:
            s.remove(cur_user)
            with open('subscribers.txt','wb') as subscribers:
                pickle.dump(s, subscribers)
        else:
            return -2

    def heritage(self, time):
        print('running heritage')
        while True:
            results = self._find_group(name=HOME)
            bot_testing = self._find_group(name=REPOSITORY)
            self.bot_testing_channel = bot_testing[1]

            if not results:
                return
            
            q = [results]
            found = set()
            while q:
                cur = q.pop()
                print('looking at: ' +  cur[0])
                self.groups[cur[0]] = cur[1]
                for message in self.get_msgs(cur[0]):

                    if not message:
                        continue
                    result = link.search(message)

                    if result:
                        
                        mid,share = result.groups(1)
                        name, gid = self.join(mid,share)

                        

                        if name:
                            if gid not in found:
                                found.add(gid)
                                q.append((name, gid))
                                

            # now generate people list based on folks in HOME
            self.people = dict([(member['nickname'], member['user_id'])
                                for member in self._get_members(results[1])])
            
            print('starting heritage sleep')
            if time == 0:
                return
            sleep(time)
            print('ending heritage sleep')

    def cat_facts(self, time):

        while True:
            print('sending cat facts')
            with open('subscribers.txt','rb') as subscribers:
                s = pickle.load(subscribers)
            response = requests.get('https://catfact.ninja/fact',
                                    headers={'Accept': 'application/json'})

            fact = response.json()['fact']
            for user_id in s:
                self.send_msg(user_id, fact)

            sleep(time)


    @staticmethod
    def _find_group(name=None, group_id=None):
        if name:
            params = {'page': 1, 'per_page':100}
            groups = [None]
            while groups:
                groups = requests.get(base + '/groups',params=params, headers=headers).json()['response']


                for group in groups:
                    if group['name'] == name:
                        group_id = group['group_id']

                        return name, group_id

                params['page'] += 1
                



        elif group_id:
            resp = requests.get(base + '/groups/'+group_id, headers=headers).json()
            name = resp['response']['name']
            return name, group_id


    def get_msgs(self, group_name):
        if group_name not in self.groups:
            return

        group_id = self.groups[group_name]
        params ={'limit': 100}
        response = requests.get(base + '/groups/'+group_id+'/messages',
                                headers = headers, params=params).json()
        
        code = response['meta']['code']
        
        if code != 304:
            messages = response['response']['messages']

        if not messages:
            raise StopIteration
        
        params['before_id'] = messages[-1]['id']


        while code != 304:
            for message in messages:
                yield message['text']
            try:
                messages = requests.get(base + '/groups/'+group_id+'/messages',
                                        headers = headers, params=params).json()['response']['messages']
            except json.decoder.JSONDecodeError:
                raise StopIteration
            if messages:
                params['before_id'] = messages[-1]['id']



    @staticmethod
    def _get_members(group_id):
        members = requests.get(base + '/groups/'+group_id,headers=headers).json()['response']['members']

        for member in members:
            yield member
            



            
    @staticmethod
    def join(mid, share):
        temp = requests.post('https://v2.groupme.com/groups/'+mid+'/join/'+share, headers=headers)


        if temp.json()['meta']['code'] == 404:
            return None, None

        temp2 = temp.json()['response']['group']
        return temp2['name'], temp2['id']

    def name(self, uid_t):
        for name,uid in self.people.items():
            if uid == uid_t:
                return name




    def ban(self, user_name):

        if user_name not in self.people:
            return -2

        u_id = self.people[user_name]
        
        with open('banned.txt', 'rb') as banned:
            ban_list = pickle.load(banned)

            if u_id in ban_list:
                return -1

            ban_list.add(u_id)

        with open('banned.txt', 'wb') as banned:
            pickle.dump(ban_list, banned)

    def unban(self, user_name):

        if user_name not in self.people:
            return -2

        u_id = self.people[user_name]

        with open('banned.txt', 'rb') as banned:
            ban_list = pickle.load(banned)

            if u_id not in ban_list:
                return -1

            ban_list.remove(u_id)


        with open('banned.txt', 'wb') as banned:
            pickle.dump(ban_list, banned)
        
        
api = API()
#api.heritage(3600)
