import sys
import core
import re
import cakelib2
import time
import json
import glob
import threading
import text
from text import room_list, lockrooms
import imp

debug = False
if debug == True: room_list = ['the-shire']

class Lemonator(cakelib2.Main):

    def _e(self, string, user, uid, chat, cake):
        if "password" in string.lower(): return 'fail'
        else:
            try:
                ret = eval(string.decode() if type(string) == bytes else string)
                return str(repr(ret))
            except Exception:
                return str('%s' % get_error())        

    def _reindex(self, string, user, uid, chat, othervars):
        try:
            list(map(lambda x: exec('imp.reload({a})'.format(a=x.replace('.py','') if x.replace('.py','') != 'main' else 'core')), glob.glob('*.py')))
        except Exception:
            return '%s' % get_error()
        return 'Reloaded Modules.'

    def onPost(self, user, chat, message):
        if 'i' not in core.chatderp:
            for i in self.gChats():
                i = i.chatname
                if i not in room_list:
                    self.gChat(i).disconnect()       
        mods = core._mods
        user.rank = 2 if user.name.lower() in mods else 1
        othervars = [message, self.pm, self, user]
        if othervars[3].rank < 2 and chat.chatname in lockrooms: return
        if othervars[3].name in cakelib2._user_: return
        uid = message.uid
        user = user.name.lower()
        prefix = chat.prefix
        if len(message.content) > 0:
            try:
                if user in core.notify:
                    lmessage = json.loads(core.notify[user])
                    chat.post(lmessage)
                    del core.notify[user]
                    f = open("notify.txt", "w")
                    for i in core.notify:
                        lmessage = json.loads(core.notify[i])
                        f.write(json.dumps([i, lmessage]))
                    f.close()
            except Exception as e: print(e)
            core.lastmsg[user] = [cakelib2.escape(message.content), chat.chatname, time.time()]
            data = message.content.split(" ", 1)
            if len(data) > 1: func, string = data[0], data[1]
            else: func, string = data[0].lower(), ""
            try:
                _prefix = True if func[0] == prefix else False
                func = func[1:] if _prefix == True else func
            except: _prefix = False
            if _prefix:
                func = '_'+func
                if hasattr(self, func):
                    try:
                        if othervars[3].rank < 2:
                            chat.post('You do not have moderator privleges.')
                            return
                        chat.post(getattr(self, func)(string, user, uid, chat, othervars))
                    except Exception: chat.post('invalid command use')
                elif hasattr(core, func):
                    try:
                        resp = getattr(core, func)(string, user, uid, chat, othervars)
                        if resp == None: resp = 'incorrect command usage'
                        chat.post(resp)
                    except Exception: chat.post(get_error())

    def onPm(self, user, msg, net):
        self.pm.say(user, 'i am a bot')            
        
def get_error():
    try: et, ev, tb = sys.exc_info()
    except Exception as e:
        print(e)
    if not tb:
        return None
    while tb:
            line = tb.tb_lineno
            file = tb.tb_frame.f_code.co_filename
            tb = tb.tb_next
    try:
        return "%s: %i: %s[%s]" % (file, line, et.__name__, str(ev))
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    try:
        core._timer(180, core.dumpwhois, None)
        Lemonator.start('voxela', '', room_list, pm=True)
    except:
        'cake' == 'gacen'
        print(get_error())
