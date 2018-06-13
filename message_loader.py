from groupy.client import Client, attachments
import re
import os

NIST_ID = '41065684'
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
        self.nist = self.retrieve_nist(NIST_ID)
        self.gen_groups()
        self.bot, self.bot_group = self.gen_bots()
        self.gen_usrs()
        #self.group_list, self.usr_list


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

    def gen_usrs(self):
        self.usr_list = {}
        for usr in self.nist.members:
            self.usr_list[usr.user_id] = usr

    def gen_bots(self):
        for b in self.myself.bots.list():
            if b.name == BOT_NAME:
                for m in self.myself.groups.list_all():
                    if m.group_id == b.group_id:
                        return b, m

    def msg_bot(self, msg):
        self.bot.post(text=msg)

    def send_message(self, msg, dest):
        if dest in self.group_list:
            self.group_list[dest].post(text=msg)

    def send_pm(self, dest, msg):
        if dest in self.usr_list:
            self.usr_list[dest].post(text=msg)

    def mesg_all(self, msg, bot_room):
        loci = []
        usr_ids = []
        for member in bot_room.members:
            loci.append([0,1])
            usr_ids.append(member.user_id)

        attachment = attachments.Mentions(loci=loci, user_ids = usr_ids)
        self.bot.post(text=msg,attachments=[attachment]) 
        
        

if __name__ == '__main__':
    m = Manager(TOKEN)
    print(m.bot_group)
