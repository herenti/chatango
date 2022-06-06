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
from os import listdir
from text import notify, rmind, room_list, jsonrooms, _mods, _board, lockrooms

weighted_choice = lambda s : random.choice(sum(([v]*wt for v,wt in s),[]))
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
banned_terms = ['bannedtermshere']
lang = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-cn', 'chinese (traditional)': 'zh-tw', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'he', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'korean': 'ko', 'kurdish (kurmanji)': 'ku', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt', 'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar (burmese)': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'scots gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}

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

def task_create(name, function, *args):
    task = newObject(**{
        'function': function,
        'var': True
        })
    objects[name] = task
    def set_timeout(name, *args):
        v = objects[name]
        while v.var == True:
            v.function(*args)
    threading.Thread(target=set_timeout, args=(name, args), daemon = True).start()

def stop_task(name):
    v = objects[name]
    v.var = 0
    del objects[name]
        
def aichat(x, user, uid, roomname, othervars):
    try: session_id = session_dict[user]
    except:
        session_id = random.randrange(1000000, 9999999)
        session_dict[user] = session_id        
    x = kernel.respond(x, session_id)
    return x
        
def nom(x, user, uid, roomname, othervars):
    person, message = x.split(' ',1)
    othervars[1].say(person, message)
    return 'PM sent.'

def _notify(x):
    notify[x] = json.dumps(x+' new mail is available. do inbox show then inbox check numberhere')
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

def mail(x, user, uid, roomname, othervars):
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
            return "I will mail %s that." % gender(name)
    except Exception as e:
            return '%s' % e

def inbox(x, user, uid, roomname, othervars):
    try:
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
            name, msg, _user, stime = json.loads(rmind[x[1]])
            del rmind[x[1]]
            f = open("rmind.txt", "w")
            for i in rmind:
                    _name, _msg, __user, _stime = json.loads(rmind[i])                                        
                    f.write(json.dumps([i, _name, _msg, __user, _stime])+"\n")
            f.close()
            return 'Message from %s to %s: %s - sent %s ago.' % (_user, name, msg, getSTime(float(stime)))
    except: return 'fail'

def yt(vid, user, uid, roomname, othervars):
    for i in vid.split():
        if i in banned_terms:
            return 'no u'
    vid = urllib.parse.quote(vid.replace(" ", "+"))
    _url = ("https://www.googleapis.com/youtube/v3/search?q=/%s&part=snippet&key=%s") % (vid, 'AIzaSyB8ENXAItE6S7GLBocixQJMUAVHMOepwuk')
    _data = urllib.request.urlopen(_url)
    data = _data.read().decode("utf-8")
    _data.close()
    data = json.loads(data)
    _i = []
    if data["pageInfo"]["totalResults"] != 0:
        for x in data["items"]:
            if "videoId" in x["id"]:
                _i.append(x)
        video = _i[0]
        video_info = video["snippet"]
        link = "http://www.youtube.com/watch?v=%s" % (video["id"]["videoId"])
        title = video_info["title"]
        return '[%s]<br/><br/>%s' % (title, link)
    else:
        return 'no results'

def gws(x, user, uid, roomname, othervars):
    try:
        for i in x.split():
            if i in banned_terms:
                return 'no u'
        x = urllib.parse.quote(x.replace(" ", "+"))
        _url = ('https://www.googleapis.com/customsearch/v1?key=%s&cx=fbd2fe34e5392ec2a&safe=off&q=%s' % ('AIzaSyB8ENXAItE6S7GLBocixQJMUAVHMOepwuk', x))
        _data = urllib.request.urlopen(_url)
        data = _data.read().decode("utf-8")
        _data.close()
        data = json.loads(data)
        results = []
        for i in data['items']:
            link = i['link']
            results.append(link)
        results = results[:4]
        return '<br/><br/>' + '<br/>'.join(results)
    except:
        return 'fail'

def gis(x, user, uid, roomname, othervars):
    for i in x.split():
        if i in banned_terms:
            return 'no u'
    x = urllib.parse.quote(x.replace(" ", "+"))
    _url = ('https://www.googleapis.com/customsearch/v1?key=%s&cx=e4944556d694be885&safe=off&num=10&searchType=image&q=%s' % ('AIzaSyB8ENXAItE6S7GLBocixQJMUAVHMOepwuk', x))
    _data = urllib.request.urlopen(_url)
    data = _data.read().decode("utf-8")
    _data.close()
    data = json.loads(data)
    results = []
    if int(data["queries"]["request"][0]["totalResults"]) != 0:
        for i in data['items']:
            link = i['link']
            results.append(link)
        return random.choice(results)
    else:
        return 'no images found'            

def tran(x, user, uid, roomname, othervars):
    try:
        for i in x.split():
            if i in banned_terms:
                return 'no u'
        dest, _text = x.split(' ',1)
        if dest in lang.keys():
            dest = lang[dest]
        if dest not in lang.values():
            return 'Invalid language'
        try:
            qs = urllib.parse.quote(_text)
        except:
            qs = urllib.parse.quote(_text.encode('utf8'))
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl=auto&tl=%s&q=%s' % (dest, qs)
        data = opener.open(url)
        _data = json.loads(data.read().decode())
        data.close()
        return _data[0][0][0]
    except:
        return 'translation fail'
    
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
    ret = roomname.whois(x.lower())
    if len(ret) > 0:
        return ', '.join(ret)
    else:
        return 'no accounts for that user yet'

def dumpwhois(x):
    f = open("whois.txt", "w")
    for i in cakelib2.uids:
           _uid = json.loads(cakelib2.uids[i])
           f.write(json.dumps([i, _uid])+"\n")                                        
    f.close()

def post(x, user, uid, roomname, othervars):
    try:
            keylist = list('12345678910@$&*^#!abcdefghijklmnopqrstuvwxyz')
            key = ''.join([random.choice(keylist) for x in range(6)])
    except Exception as e: print(e)
    if len(_board.keys()) > 11:
        for i in _board:
            del _board[i]
    x = '%s - <font color="#00ffff"><b>%s</b></font>: %s' % (time.strftime('%c'), user, x)
    _board[key] = json.dumps(x)
    f = open("board.txt", "w")
    for i in _board:
           _post = json.loads(_board[i])
           f.write(json.dumps([i, _post])+"\n")                                        
    f.close()
    return 'Posted to the board.'

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

def bgtime(x, user, uid, chat, cake):
    resp = urllib.request.urlopen("http://st.chatango.com/profileimg/%s/%s/%s/mod1.xml" % (x.lower()[0], x.lower()[1], x.lower()))
    try: data = resp.read().decode()
    except: data = resp.read().decode('latin-1')
    resp.close()
    try: data = re.compile(r'<d>(.*?)</d>', re.IGNORECASE).search(data).group(1)
    except: return 'they have never had a background, or that is not a real user'
    data = int(data)
    if data < time.time(): return 'that users background expired: ' + getSTime(data) + ' ago'
    else:
        return 'that user has: ' + getBGTime(int(data)) + ' left'

def is_online(user):
    resp = urllib.request.urlopen("http://"+user+".chatango.com").read().decode()
    return str(bool('chat with' in resp.lower()))+ ' '+user

def cmds(x, user, uid, chat, cake):
    return 'in progress: for now: [whois, seen, bgtime, yt, gis, gws, tran, mail, inbox show/check, owner, post, board]' 

chatderp = []
chatobj = []

def owner(x, user, uid, chat, cake):
    x = x.lower()
    if cakelib2.checkG(x) == True:
        cake[2].joinChat(x)
        chatderp.append('i')
        def _owner(b):
            time.sleep(2)
            owner = cake[2].gChat(x).chatInfo.owner
            chatobj.append(cake[2].gChat(x))
            chatderp.remove('i')
            chat.post('the owner is: ' + owner)
        _task(_owner, x)
        return 'working on it'
    else: return 'that is not a real chat name'
    
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

def _task(function, *var):
    event = threading.Event()
    threading.Thread(target = function, args = (var), daemon = True).start() 

