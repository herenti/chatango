import json
import re
import urllib.request
import urllib.parse
import time
import cakelib2
import inspect
import os
import random
import html
import threading
from text import notify, rmind, room_list, jsonrooms, _mods, _board, lockrooms

weighted_choice = lambda s : random.choice(sum(([v]*wt for v,wt in s),[]))
opener = urllib.request.build_opener()
opener.addheaders=[('User-agent', 'Mozilla/5.0')]

def unescape(text): return html.unescape(text)
def escape(text): return ''.join(['&#%s;' % ord(x) for x in text])

objects = dict()
lastmsg = dict()

class newObject(object):

    def __init__(self, **kw):
        [setattr(self, x, kw[x]) for x in kw]
        self.object_ret()

    def object_ret(self): return self

def say(x, user, uid, roomname, othervars):
    return x

def keygen():
    l = list('abcdefghijklmnopqrstuvwxyz123456789!@#$%^&*()_-+={}[]|\:;?/~`"" ')
    random.shuffle(l)
    return l

def encrypt(x):
    key = keygen()
    y = list('abcdefghijklmnopqrstuvwxyz123456789!@#$%^&*()_-+={}[]|\:;?/~`"" ')
    z = dict(zip(y, key))
    l = []
    for match in list(x):
        l.append(match.replace(match, z[match]))
    return (''.join(key), ''.join(l))

def decrypt(key, x):
    key = list(key)
    y = list('abcdefghijklmnopqrstuvwxyz123456789!@#$%^&*()_-+={}[]|\:;?/~`"" ')
    z = dict(zip(key, y))
    l = []
    for match in list(x):
        l.append(match.replace(match, z[match]))
    return ''.join(l) 

def task_create(name, timeout, function, *args):
    task = newObject(**{
        'timeout': int(timeout),
        'function': function,
        'start': time.time(),
        'var': 1
        })
    objects[name] = task
    def set_timeout(name, *args):
        v = objects[name]
        while v.var == 1:
            time.sleep(1)
            if (time.time() - v.start) > v.timeout:
                v.function(*args)
                v.start = time.time()
    threading.Thread(target=set_timeout, args=(name, args), daemon = True).start()

def stop_task(name):
    v = objects[name]
    v.var = 0
    del objects[name]

def nom(x, user, uid, roomname, othervars):
    person, message = x.split(' ',1)
    othervars[1].say(person, message)
    return 'PM sent.'

def _notify(x):
    notify[x] = json.dumps(x+' new messages are available. If you do not know how to read messages ask myth')
    f = open('notify.txt', 'w')
    for i in notify:
            message = json.loads(notify[i])
            f.write(json.dumps([i, message])+'\n')
    f.close()

def u_rooms(chat, user, othervars):
    v = []
    w = [{x: othervars[2].gChat(x).chatInfo.userlist} for x in room_list]
    for y in range(len(room_list)):
            for z in w[y]:
                    if user in w[y][z]: v.append(z)
    return v

def seen(x, user, uid, roomname, othervars):
    try:
            name = x.lower()
            msg, room, seentime = lastmsg[name]
            msg = unescape(msg)
            urooms = u_rooms(roomname, name, othervars)
            if room in urooms: urooms.remove(room)
            ret = "<b>%s</b> was last seen in <b>%s</b> %s ago saying <b>%s</b>." % (name, room, getSTime(float(seentime)), msg) if is_online(name) != False else "<b>%s</b> was last seen leaving <b>%s</b> %s ago saying <b>%s</b>." % (name, room, getSTime(float(seentime)), msg)
            if len(urooms) > 0:
                    part = 'rooms' if len(urooms) > 1 else 'room'
                    ret += ' This user is also in the %s: %s' % (part, ', '.join(urooms))# if len(urooms) > 1 else ''
    except KeyError: ret = 'I have not recorded any messages from that account.'
    return ret

def remind(x, user, uid, roomname, othervars):
    try:
            mid = str(random.randrange(1000, 9999))
            name, message = x.split(' ',1)
            name = name.lower()
            stime = time.time()
            rmind[mid] = json.dumps([name, message, user, stime])
            _notify(name)
            f = open("rmind.txt", "w")
            for i in rmind:
                name, msg, _user, stime = json.loads(rmind[i])                                        
                f.write(json.dumps([i, name, msg, _user, stime])+"\n")
            f.close()
            return "I will remind %s that." % gender(name)
    except Exception as e:
            return '%s' % e

def inbox(x, user, uid, roomname, othervars):
    x = x.lower().split(' ')
    y = []
    if len(x) < 1: return 'Incorrect command usage.'
    if x[0] == 'show':
            for i in rmind:
                  name, msg, _user, stime = json.loads(rmind[i])
                  if name == user: y.append('#<font color="#00ffff"><b>[</b></font>'+i+'<font color="#00ffff"><b>]</b></font>' + ': from - '+_user)
            ret = '<br /><br />'+'<br />'.join(y) if len(y) > 0 else 'no messages found'
            return ret
    elif x[0] == 'check':
            try:
                    name, msg, _user, stime = json.loads(rmind[x[1]])
                    del rmind[x[1]]
                    f = open("rmind.txt", "w")
                    for i in rmind:
                            _name, _msg, __user, _stime = json.loads(rmind[i])                                        
                            f.write(json.dumps([i, _name, _msg, __user, _stime])+"\n")
                    f.close()
                    return 'Message from %s to %s: %s - sent %s ago.' % (_user, name, msg, getSTime(float(stime)))
            except KeyError: return 'Fail'

def gws(x, user, uid, roomname, othervars):
    search = x.split()
    search = '%20'.join(map(str, search))
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&safe=off' % search
    search_results = urlreq.urlopen(url)
    js = json.loads(search_results.read().decode())
    rest = list(map(lambda x: x['unescapedUrl'], js['responseData']['results']))
    rest = '<br /><br />' + '<br />'.join(rest)
    return rest

def getBGTime(x):
    total_seconds = float(x - time.time())
    MIN     = 60
    HOUR    = MIN * 60
    DAY     = HOUR * 24
    YEAR    = DAY * 365.25
    years   = int( total_seconds / YEAR )       
    days    = int( (total_seconds % YEAR ) / DAY  )
    hrs     = int( ( total_seconds % DAY ) / HOUR )
    min = int( ( total_seconds  % HOUR ) / MIN )
    secs = int( total_seconds % MIN )
    string = ""
    if years > 0: string += "<font color='#00ffff'>" + str(years) + "</font> " + (years == 1 and "year" or "years" ) + ", "
    if len(string) > 0 or days > 0: string += "<font color='#00ffff'>" + str(days) + "</font> " + (days == 1 and "day" or "days" ) + ", "
    if len(string) > 0 or hrs > 0: string += "<font color='#00ffff'>" + str(hrs) + "</font> " + (hrs == 1 and "hour" or "hours" ) + ", "
    if len(string) > 0 or min > 0: string += "<font color='#00ffff'>" + str(min) + "</font> " + (min == 1 and "minute" or "minutes" ) + " and "
    string += "<font color='#00ffff'>" +  str(secs) + "</font> " + (secs == 1 and "second" or "seconds" )
    return string

def getSTime(x):
    total_seconds = float(time.time() - x)
    MIN     = 60
    HOUR    = MIN * 60
    DAY     = HOUR * 24        
    days    = int( total_seconds / DAY )
    hrs     = int( ( total_seconds % DAY ) / HOUR )
    min = int( ( total_seconds  % HOUR ) / MIN )
    secs = int( total_seconds % MIN )
    string = ""
    if days > 0: string += "<font color='#00ffff'>" + str(days) + "</font> " + (days == 1 and "day" or "days" ) + ", "
    if len(string) > 0 or hrs > 0: string += "<font color='#00ffff'>" + str(hrs) + "</font> " + (hrs == 1 and "hour" or "hours" ) + ", "
    if len(string) > 0 or min > 0: string += "<font color='#00ffff'>" + str(min) + "</font> " + (min == 1 and "minute" or "minutes" ) + " and "
    string += "<font color='#00ffff'>" +  str(secs) + "</font> " + (secs == 1 and "second" or "seconds" )
    return string

def name_color_gen():
    clist, i, color = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'], 0, []
    while (i < 6): color.append(random.choice(clist)); i+=1
    return ''.join(color)

def whois(x, user, uid, roomname, othervars):
    return roomname.whois(x.lower())

def dumpwhois(x):
    f = open("whois.txt", "w")
    for i in cakelib2.uids:
           _uid = json.loads(cakelib2.uids[i])
           f.write(json.dumps([i, _uid])+"\n")                                        
    f.close()
    print('dumped whois info')

def post(x, user, uid, roomname, othervars):
    try:
            keylist = list('12345678910@$&*^#!abcdefghijklmnopqrstuvwxyz')
            key = ''.join([random.choice(keylist) for x in range(6)])
    except Exception as e: print(e)
    if len(_board.keys()) < 11:
            x = '%s - <font color="#00ffff"><b>%s</b></font>: %s' % (time.strftime('%c'), user, x)
            _board[key] = json.dumps(x)
            f = open("board.txt", "w")
            for i in _board:
                   _post = json.loads(_board[i])
                   f.write(json.dumps([i, _post])+"\n")                                        
            f.close()
            return 'Posted to the board.'
    else: return 'The board is too large, so please delete some posts.'

def board(x, user, uid, roomname, othervars):
    y = [json.loads(_board[x]) for x in _board]
    return '<br/><br/>'+ '<br/>'.join(y)

def gender(x):
    resp = urllib.request.urlopen("http://st.chatango.com/profileimg/%s/%s/%s/mod1.xml" % (x.lower()[0], x.lower()[1], x.lower()))
    try: data = resp.read().decode()
    except: data = resp.read().decode('latin-1')
    try: ru = re.compile(r'<s>(.*?)</s>', re.IGNORECASE).search(data).group(1)
    except: ru = "?"
    ret = urllib.parse.unquote(ru)
    if ret == "M": r = "him"
    elif ret == "F": r = "her"
    elif ret == "?": r = "them"        
    return r

def is_online(user):
    resp = urllib.request.urlopen("http://"+user+".chatango.com").read().decode()
    return str(bool('chat with' in resp.lower()))+ ' '+user
    
def rmanage(x, user, uid, chat, cake):
    x = x.lower()
    if len(x.split(' ')) > 1:
        x = x.split(' ')
        func, _room = x[0], x[1]
    else:
        func = x        
    if cake[3].rank < 2: return 'You do not have moderator permissions.'
    else:
        if func == 'list':
            derp = []
            for i in room_list:
                if i in lockrooms: i = '<font color="#ff0000"><b>' + i + '</b></font>'
                else: i = '<font color="#00ff00"><b>' + i + '</b></font>'
                derp.append(i)    
            return ', '.join(derp)
        elif func == 'join':
            if _room not in room_list:
                if cakelib2.checkG(_room) == True:
                    cake[2].joinChat(_room)
                    room_list.append(_room)
                    roomname = _room
                    joiner = user
                    jointime = time.time()
                    roomlock = 'False'
                    locker = 'none'
                    locktime = 'none'
                    jsonrooms[roomname] = json.dumps([joiner, roomlock, jointime, locker, locktime])
                    f = open("jsonrooms.txt", "w")
                    for i in jsonrooms:
                        joiner, roomlock, jointime, locker, locktime = json.loads(jsonrooms[i])
                        f.write(json.dumps([i, joiner, roomlock, jointime, locker, locktime])+"\n")                                        
                    f.close()
                    return 'joined ' + _room
                else: return 'That is not a real group'
            else: return 'I am already in that group'
        elif _room in room_list:
            if func == 'leave':
                del jsonrooms[_room]
                cake[2].gChat(_room).disconnect()
                room_list.remove(_room)
                if _room in lockrooms: lockrooms.remove(_room)
                f = open("jsonrooms.txt", "w")
                for i in jsonrooms:
                    joiner, roomlock, jointime, locker, locktime = json.loads(jsonrooms[i])
                    f.write(json.dumps([i, joiner, roomlock, jointime, locker, locktime])+"\n")                                        
                f.close()
                return 'I have left ' + _room
            elif func == 'lock':
                lockrooms.append(_room)
                joiner, roomlock, jointime, locker, locktime = json.loads(jsonrooms[_room])
                roomlock = 'True'
                locker = user
                locktime = time.time()
                jsonrooms[_room] = json.dumps([joiner, roomlock, jointime, locker, locktime])
                f = open("jsonrooms.txt", "w")
                for i in jsonrooms:
                    joiner, roomlock, jointime, locker, locktime = json.loads(jsonrooms[i])
                    f.write(json.dumps([i, joiner, roomlock, jointime, locker, locktime])+"\n")                                        
                f.close()
                return 'locked ' + _room
            elif func == 'unlock':
                if _room in lockrooms:
                    lockrooms.remove(_room)
                    joiner, roomlock, jointime, locker, locktime = json.loads(jsonrooms[_room])
                    roomlock = 'False'
                    locker = user
                    locktime = time.time()
                    jsonrooms[_room] = json.dumps([joiner, roomlock, jointime, locker, locktime])
                    f = open("jsonrooms.txt", "w")
                    for i in jsonrooms:
                        joiner, roomlock, jointime, locker, locktime = json.loads(jsonrooms[i])
                        f.write(json.dumps([i, joiner, roomlock, jointime, locker, locktime])+"\n")                                        
                    f.close()
                    return 'unlocked ' + _room
            elif func == 'check':
                joiner, roomlock, jointime, locker, locktime = json.loads(jsonrooms[_room])
                if roomlock == 'True':
                    return 'locked by %s %s ago. [Joined by %s %s ago]' % (locker, getSTime(locktime), joiner, getSTime(jointime))
                elif roomlock == 'False' and locker != 'none':
                    return 'unlocked by %s %s ago. [Joined by %s %s ago]' % (locker, getSTime(locktime), joiner, getSTime(jointime))
                elif locktime == 'none': return 'that room has not been locked yet. [Joined by %s %s ago]' % (joiner, getSTime(jointime))
            else: return 'Invallid command use'
        else: return 'derp'
    
def mod(x, user, uid, roomname, othervars):
    x = x.lower()
    try: func, args = x.split(' ',1)
    except ValueError: func = x
    if func == 'list': return ', '.join(_mods)
    if othervars[3].rank < 2: return 'You do not have moderator permissions.'
    if othervars[3].rank > 1:
            if func == 'add':
                if args in _mods: return 'That user is already modded.'
                else: _mods.append(args)
            elif func == 'remove':
                if args not in _mods: return 'That user is not modded.'
                else: _mods.remove(args)
            else: return None
            f = open('mods.txt', 'w')
            for i in _mods:
                    f.write(i+'\n')
            f.close()
            resp = 'Added %s to the mods list.' % args if func == 'add' else 'Removed %s from the mods list.' % args
            return resp

def _timer(seconds, function, *var):
    event = threading.Event()
    def decorator(*var):
        while not event.wait(seconds): function(*var)
    threading.Thread(target = decorator, args = (var), daemon = True).start()
    return 
