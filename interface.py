from groupy.client import Client, attachments
import re
import os

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
        self.bots = dict([(bot.bot_id,bot) for bot in self.myself.bots.list()])


    def retrieve_nist(self, uid):
        # retrieve main group chat
        for group in self.myself.groups.list_all():
            if group.name == HOME:
                # this is SURF 2018
                return group

            
    def gen_groups(self):
        group_queue = [self.nist]
        self.group_list = {}
        while group_queue:
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
                        except Exception:
                            continue
                        if joined:
                            group_queue.append(joined)
                        self.group_list[joined.id] = joined
        
                        
    def gen_usrs(self):
        self.usr_list = {}
        for usr in self.nist.members:
            self.usr_list[usr.user_id] = usr

        
def setup():
    return Manager("61QyU38rd2gpRrGDxK7obK1Re4QrcPelyIKp9EEn")

if __name__ == '__main__':
    m = Manager(TOKEN)
    print(m.bots)
