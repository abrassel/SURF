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
        self.groups = {}
        self.people = {}
        self.load()
        self.t_heritage   = Thread(target=self.heritage,   args=(30*60,))
        self.t_cat_facts  = Thread(target=self.cat_facts,  args=(30,))
        self.t_state_save = Thread(target=self.state_save, args=(20*60,))

    
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
        data = {'name':name}

        requests.post(base + '/groups',
                      headers=headers,
                      data=data)
        
    @staticmethod
    def list_members(group):
        results = requests.get(base + '/groups/'+self.groups[group]).json()


    def subscribe(self, new_user):
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
        while True:
            results = self._find_group(name=HOME)
            q = [results]

            while q:
                cur = q.pop()
                self.groups[cur[0]] = cur[1]

                for message in self.get_msgs(cur[0]):
                    result = link.search(message)

                    if result:
                        mid,share = result.groups(1)
                        name, gid = self.join(mid,share)

                        if name:
                            q.append((name, gid))
            



            
            sleep(time)

    def cat_facts(self, time):
        while True:
            response = requests.get('https://catfact.ninja/fact',
                                    headers={'Accept': 'application/json'})

            fact = response.json()['fact']
            for user_id in self.subscribers:
                self.send_msg(user_id, fact)

            sleep(time)

    def state_save(self, time):
        while True:
            
            # first, save subscribers
            pickle.dump(self.subscribers,
                        'subscribers.txt')

            # next, save the group list
            pickle.dump(self.groups,
                        'groups.txt')

            # finally, save the people
            pickle.dump(self.people,
                        'people.txt')

            sleep(time)

    def load(self):
        self.subscribers = pickle.load('subscribers.txt')
        self.groups = pickle.load('groups.txt')
        self.people = pickle.load('people.txt')
