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

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'X-Access-Token': os.environ.get('token'),
}

base = 'https://api.groupme.com/v3'

class API:
    def __init__(self):
        try:
            self.load()
        except (TypeError, FileNotFoundError):
            print('started')
            self.subscribers = set()
            self.people = {}
            self.groups = {}
            self.t_heritage   = Thread(target=self.heritage,   args=(30*60,)).start()
            self.t_cat_facts  = Thread(target=self.cat_facts,  args=(30,)).start()
            self.t_state_save = Thread(target=self.state_save, args=(20*60,)).start()

    
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

    @staticmethod
    def create_group(name):
        data = {'name':name,
                'share': True}

        reply = requests.post(base + '/groups',
                              headers=headers,
                              data=json.dumps(data)).json()
        self.groups[name] = reply['response']['group_id']
        
    @staticmethod
    def list_members(group):
        results = requests.get(base + '/groups/'+self.groups[group]).json()


    def subscribe(self, new_user):
        if new_user not in self.people:
            if new_user not in self.people:
                return -2

        
        user_id = self.people[new_user]
        if user_id in self.subscribers:
            return -1


        self.subscribers.add(user_id)
        
    def unsubscribe(self, cur_user):
        
        if cur_user not in self.subscribers:
            return -1

        if random() > .75:
            self.subscribers.remove(cur_user)
            
        else:
            return -2

    def heritage(self, time):
        print('running heritage')
        while True:
            results = self._find_group(name=HOME)

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
        print('sending cat facts')
        while True:
            response = requests.get('https://catfact.ninja/fact',
                                    headers={'Accept': 'application/json'})

            fact = response.json()['fact']
            for user_id in self.subscribers:
                self.send_msg(user_id, fact)

            sleep(time)

    def state_save(self, time):
        print('saving state')
        while True:
            with open('subscribers.txt','wb') as subscribers:
                # first, save subscribers
                pickle.dump(self.subscribers,
                            subscribers)
            with open('groups.txt','wb') as groups:
                # next, save the group list
                pickle.dump(self.groups,
                            groups)

            with open('people.txt','wb') as people:
                # finally, save the people
                pickle.dump(self.people,
                            people)

            sleep(time)

    def load(self):
        with open('subscribers.txt','rb') as subscribers:
            # first, save subscribers
            self.subscribers = pickle.load(subscribers)
        with open('groups.txt','rb') as groups:
            # next, save the group list
            self.groups = pickle.load(groups)

        with open('people.txt','rb') as people:
            # finally, save the people
            self.people = pickle.load(people)

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

        
        
api = API()
#api.heritage(3600)
