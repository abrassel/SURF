from groupy.client import Client
import re

NIST_ID = '41065684'
TOKEN = "61QyU38rd2gpRrGDxK7obK1Re4QrcPelyIKp9EEn"
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
        self.nist = self.retrieve_nist(NIST_ID)
        self.gen_groups()
        self.bot, self.bot_group = self.gen_bots()


    def retrieve_nist(self, uid):
        # retrieve main group chat
        for group in self.myself.groups.list_all():
            if group.id == NIST_ID:
                # this is SURF 2018
                return group

            
    def gen_groups(self):
        self.group_list = {}
        for m in self.nist.messages.list_all():
            if m and m.text:
                # have found a candidate string, now parse link out
                result = self.link.search(m.text)
                if result:
                    mid,share = result.groups(1)
                    joined = self.myself.groups.join(mid,share)
                    self.group_list[joined.id] = joined

    def gen_bots(self):
        for b in self.myself.bots.list():
            if b.name == BOT_NAME:
                for m in self.myself.groups.list_all():
                    if m.group_id == b.group_id:
                        return b, m

    def msg_bot(self, msg):
        self.bot.post(text=msg)

    def send_message(self, msg, dest):
        self.group_list[dest].post(text=msg)
        

if __name__ == '__main__':
    m = Manager(TOKEN)
    print(m.bot_group)
