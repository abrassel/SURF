from groupy.client import Client, attachments
import re
import os
from collections import defaultdict

HOME="Bot Testing Channel"
#HOME = '41065684'
TOKEN = os.environ.get('token', None)
BOT_NAME = 'testbot'

class Manager:
    '''
    link: the regex match for a share link
    myself: the client instance
    nist: the main nist group chat
    group_list: list of NIST groups indexed by group ID
    bot: the active bot (in this case test bot)
    '''
    def __init__(self, uid):
        self.link = re.compile('https://groupme.com/join_group/(\d+)/(\S+)')
        self.myself = Client.from_token(uid)
        self.nist = self.retrieve_nist(HOME)
        self.gen_groups()
        self.gen_usrs()
        self.bots = dict([(bot.group_id,bot) for bot in self.myself.bots.list()])
        # gen owners
        self.owners = {}
        for room in self.group_list.values():
            self.gen_owner(room)

        self.privileged = defaultdict(lambda: False)
        


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
        
                        
    def gen_usrs(self):
        self.usr_list = {}
        for usr in self.nist.members:
            self.usr_list[usr.user_id] = usr

    def gen_owner(self, room):
        for member in room.members:
            if "owner" in member.roles:
                self.owners[room.group_id] = member
                return

    def is_owner(self, user_id, room):
        return room in self.owners and user_id == self.owners[room].user_id

        

if __name__ == '__main__':
    m = Manager(TOKEN)
    print(m.bots)
