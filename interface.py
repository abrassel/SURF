from groupy.client import Client, attachments
from groupy.api.bots import Bots
import re
import os
from collections import defaultdict
from time import sleep
import json
import requests
from threading import Timer

HOME="Bot Testing Channel"
#HOME = '41065684'
TOKEN = os.environ.get('token', None)
BOT_NAME = 'testbot'
alive = 15 # 25 * 60
cat_facts = 30 * 60
auto_update = 24 * 60 * 60

class Manager:
    '''
    link: the regex match for a share link
    myself: the client instance
    nist: the main nist group chat
    group_list: list of NIST groups indexed by group ID
    bot: the active bot (in this case test bot)
    '''
    def __init__(self, uid):
        self.link = re.compile('https://\S*.?groupme.com/join_group/(\d+)/(\S+)')
        self.myself = Client.from_token(uid)
        self.nist = self.retrieve_nist(HOME)
        self.gen_groups()
        self.bots = dict([(bot.group_id,bot) for bot in self.myself.bots.list()])
        # gen owners
        self.owners = {}
        for room in self.group_list.values():
            self.gen_owner(room)

        self.privileged = defaultdict(lambda: False)
        self.muted = defaultdict(lambda: False)
        self.cat_facts_list = {}
        self.launch_cat_facts()
        #self.launch_auto_update()
        self.launch_keep_alive()

    def launch_cat_facts(self):
        Timer(cat_facts, self.launch_cat_facts).start()
        print('sending cat facts')
        self.send_cat_facts()

    def launch_auto_update(self):
        Timer(auto_update, self.launch_auto_update).start()
        self.update()

    def launch_keep_alive(self):
        Timer(alive, self.launch_keep_alive).start()
        requests.get("https://surf-bot-1998.herokuapp.com/")
        print('posting keep-alive')
        

        
    def retrieve_nist(self, uid):
        # retrieve main group chat
        for group in self.myself.groups.list_all():
            if group.name == HOME or group.id == HOME:
                # this is SURF 2018
                return group

            
    def gen_groups(self):
        group_queue = [self.nist]
        self.group_list = {self.nist.group_id:self.nist}
        while group_queue:
            try:
                cur = group_queue.pop()
                if not cur:
                    continue
                for m in cur.messages.list_all():
                    if m and m.text:
                        # have found a candidate string, now parse link out
                        result = self.link.search(m.text)
                        if result:
                            mid,share = result.groups(1)
                            try:
                                joined = self.myself.groups.join(mid,share)
                            except:
                                print('an exception has been caught')
                                continue
                            if joined and joined.group_id not in self.group_list:
                                group_queue.append(joined)
                                self.group_list[joined.group_id] = joined
            except Exception:
                continue
            
    def update(self, groups=None, new_bots=None):
        if groups:
            for group in groups:
                self.group_list[group.group_id] = group
                for member in group.members:
                    if "owner" in member.roles:
                        self.owners[group.group_id] = member
                        break

            self.bots = dict([(bot.group_id,bot) for bot in self.myself.bots.list()])

        if new_bots:
            for bot in new_bots:
                self.bots[bot.group_id] = bot

        elif not groups and not new_bots:
            self.gen_groups()
            self.bots = dict([(bot.group_id,bot) for bot in self.myself.bots.list()])
            # gen owners
            self.owners = {}
            for room in self.group_list.values():
                self.gen_owner(room)

            
    def send_cat_facts(self):
        headers = {'Accept': 'application/json'}
        fact = requests.get('https://catfact.ninja/fact', headers=headers).json()['fact']

        for user in self.cat_facts_list.values():
            user.post(text=fact)
            
            

    def gen_owner(self, room):
        for member in room.members:
            if "owner" in member.roles:
                self.owners[room.group_id] = member
                return

    def is_owner(self, user_id, room):
        return room in self.owners and user_id == self.owners[room].user_id

    def join(self, chat_id, user_id, room_name):

        # get group to add to
        for group in self.group_list.values():
            if group.name == room_name:
                target = group.group_id

        # get member object, and add
        for member in self.group_list[chat_id].members:
            if member.user_id == user_id:
                member.add_to_group(target)
                return

    def create_group(self, chat_id, user_id, room_name):
        group = self.myself.groups.create(name=room_name,share=True)

        # get member
        for member in self.group_list[chat_id].members:
            if member.user_id == user_id:
                member.add_to_group(group.group_id)
                break

        sleep(3)
        group.change_owners(user_id)
        if not self.muted[chat_id]:
            self.bots[chat_id].post(text="Created group %s at %s" % (room_name,group.share_url))
            self.update(groups=[group])

    
    def create_bot(self, room_name):
        room_id = None

        for group in self.group_list.values():
            if group.name == room_name:
                room_id = group.group_id

        if not room_id:
            sleep(3)
            return self.create_bot(self, room_name)

        # their library is broken ... have to go through API myself
        url = "https://api.groupme.com/v3/bots"
        params = {'token':TOKEN}
        body = {'bot':{'name':'SURF', 'group_id': room_id, 'callback_url': 'https://surf-bot-1998.herokuapp.com'}}
        headers = {'Content-Type': 'application/json'}
        requests.post(url, params=params, headers=headers, data=json.dumps(body,indent=2))
        self.update(new_bots=self.myself.bots.list())

if __name__ == '__main__':
    m = Manager(TOKEN)
    print(m.bots)
