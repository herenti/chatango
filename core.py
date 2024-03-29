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
from text import notify, rmind, rpg_players, lastmsg, room_list, jsonrooms, _mods, __board, lockrooms

weighted_choice = lambda s : random.choice(sum(([v]*wt for v,wt in s),[]))
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
banned_terms = ['']
lang = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese-': 'zh-cn', 'chinese': 'zh-tw', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'he', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'korean': 'ko', 'kurdish': 'ku', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt', 'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar': 'my','burmese': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'scots-gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}
command_list = ['yt','say','seen','mail','e','inbox','gws','gis','tran','whois','post','board','bgtime','rmange','owner','cmds','mod','reindex','nom']
api_key = ''

def unescape(text): return html.unescape(text)
def escape(text): return ''.join(['&#%s;' % ord(x) for x in text])

objects = dict()

class newObject(object):

    def __init__(self, **kw):
        [setattr(self, x, kw[x]) for x in kw]
        self.object_ret()

    def object_ret(self): return self

def _say(x, user, uid, roomname, othervars):
    return x

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
    objects[name].var = False
    del objects[name]
        
def aichat(x, user, uid, roomname, othervars):
    try: session_id = session_dict[user]
    except:
        session_id = random.randrange(1000000, 9999999)
        session_dict[user] = session_id        
    x = kernel.respond(x, session_id)
    return x
        
def _nom(x, user, uid, roomname, othervars):
    person, message = x.split(' ',1)
    othervars[1].say(person, message)
    return 'PM sent.'

def _pfp(x, user, uid, roomname, othervars):
    try: _i, _n = x[0], x[1]
    except: _i, _n = x, x
    return 'http://ust.chatango.com/profileimg/%s/%s/%s/full.jpg' % (_i, _n, x)

def _msbg(x, user, uid, roomname, othervars):
    try: _i, _n = x[0], x[1]
    except: _i, _n = x, x
    return 'http://ust.chatango.com/profileimg/%s/%s/%s/msgbg.jpg' % (_i, _n, x)
    
def _langs(x, user, uid, roomname, othervars):
    if x == '': part = ['do langs 1, 2, or 3']
    elif x == '1': part = ['['+i+':'+lang[i]+']' for i in lang][:40]
    elif x == '2': part = ['['+i+':'+lang[i]+']' for i in lang][40:80]
    elif x == '3': part = ['['+i+':'+lang[i]+']' for i in lang][80:]
    return ', '.join(part)

def _notify(x):
    notify[x] = json.dumps(x+' new mail is available. do the inbox command')
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

def _seen(x, user, uid, roomname, othervars):
    try:
            name = x.lower()
            msg, room, seentime = json.loads(lastmsg[name])
            urooms = u_rooms(roomname, name, othervars)
            if room in urooms: urooms.remove(room)
            ret = "<b>%s</b> was last seen in <b>%s</b> %s ago saying <b>%s</b>." % (name, room, getSTime(float(seentime)), msg) if is_online(name) != False else "<b>%s</b> was last seen leaving <b>%s</b> %s ago saying <b>%s</b>." % (name, room, getSTime(float(seentime)), msg)
            if len(urooms) > 0:
                    part = 'rooms' if len(urooms) > 1 else 'room'
                    ret += ' This user is also in the %s: %s' % (part, ', '.join(urooms))# if len(urooms) > 1 else ''
    except KeyError: ret = 'I have not recorded any messages from that account.'
    return ret

clan_list = ['ethos','verity','regal','burathian','noctuo', 'dragoon']

weapon_dict = {'unarmed': '0 5 1 1 no 1 mele',
               'short sword': '100 10 1 1 no 1 mele',
               'bow': '100 13 2 1 yes 10 ranged',
               'dildo': '200 16 1 3 no 1 mele',
               'simple crossbow': '200 19 2 3 yes 10 ranged',
               'kurrik': '500 24 1 8 no 1 mele',
               'long bow': '500 24 2 8 yes 10 ranged',
               'legalace': '750 28 1 13 no 1 mele',
               'heraldi nakal': '750 32 1 13 yes 15 ranged',
               'nuke': '1000000 1000000 10000 50 yes 1 ranged',
               'jizz': '0 1 0.1 1 yes 1 ranged',
               'orc penis': '2400 36 1 17 no 1 mele',
               'nalax blade': '4320 66 1 25 no 1 mele',
               'eonir': '7776 122 1 32 no 1 mele',
               'scorch blade': '13997 230 1 40 no 1 mele',
               'flametongue': '27994 409 1 49 no 1 mele',
               'masamena': '58787 733 1 56 no 1 mele',
               'katana': '105816 1253 1 65 no 1 mele',
               'mace bolag': '190468 2263 1 69 no 1 mele',
               'goat boner': '361890 4334 1 79 no 1 mele',
               'four seasons sword': '759969 7607 1 87 no 1 mele',
               'master sword': '1443941 13483 1 98 no 1 mele',
               'thundercrotch': '2743489 24520 1 100 no 1 mele',
               'fury bow': '2400 39 2 17 yes 15 ranged',
               'spunk lobber': '4560 72 2 26 yes 15 ranged',
               'zephyr': '8208 131 2 34 yes 15 ranged',
               'bone bow': '16416 240 2 39 yes 15 ranged',
               'heraldi nakul': '29549 470 2 47 yes 15 ranged',
               'wicked crossbow': '62052 751 2 57 yes 15 ranged',
               'ashen longbow': '130310 1443 2 67 yes 15 ranged',
               'hunter bow': '260620 2595 2 76 yes 15 ranged',
               'grool launcher': '495179 4793 2 74 yes 15 ranged',
               'charred yaran': '891322 8822 2 87 yes 15 ranged',
               'nerethil': '1871776 15905 2 98 yes 15 ranged',
               'cbt inducer': '7861458 28104 2 100 yes 15 ranged'
            }

def selector(i, n):
    return random.choice(range(i, n))

def wgen():
    _lmin, _lma = 16, 20
    cost = 1200
    rate = ''
    _dmin, _dma = 36, 40
    a = []
    for i in range(80):
        level = selector(_lmin, _lma)
        _lmin, _lma = _lmin+selector(6, 10), _lma+selector(6, 10)
        cost *= selector(18, 22)/10
        damage = selector(round(_dmin), round(_dma))
        _dmin *= 1.83
        _dma *= 1.83
        if level >= 100: level = 100
        a.append(str(round(cost))+' '+str(round(damage))+' '+rate+' '+str(level) + ' yes 15 ranged')
        if level == 100: break
    return a
        

potion_dict = {'health s': '20 25 health',
               'health m': '40 50 health',
               'health l': '80 100 health',
               'health xl': '160 200 health',
               'elixer': '400 500 health',
               'godsgrow': '1000 1000 health',
               'peerless health': '2500 3000 health',
               'accuracy': '250 0.1 accuracy',
               'peerless accuracy': '2500 0.2 accuracy',
               'crit': '2500 0.2 critchance'
               }

item_dict = {'condom':'it might be used 100',
             'body pillow':'why is it stiff? 250',
             'stuffed animal':'for cuddles 100',
             'gold necklace':'fine craftmanship 1000',
             'pet cat':'this kitty chonk 500',
             'pet tiger':'it might eat you 10000',
             'pet dog':'a loyal companion!!! 500',
             'diamond earring':'sparkles like nothing else 3000',
             'wedding rings':'for the one you love [for marrying] 10000',
             'ethirium pendant':'very rare material of a mysterious nature 100000',
             'royal crest':'those with this crest will now have a royal title 1000000'
             }

max_health = {'1': 110, '2': 121, '3': 133, '4': 146, '5': 161, '6': 177, '7': 195, '8': 214, '9': 236, '10': 259, '11': 285, '12': 314, '13': 345, '14': 380, '15': 418, '16': 459, '17': 505, '18': 556, '19': 612, '20': 673, '21': 740, '22': 814, '23': 895, '24': 985,
              '25': 1083, '26': 1192, '27': 1311, '28': 1442, '29': 1586, '30': 1745, '31': 1919, '32': 2111, '33': 2323, '34': 2555, '35': 2810, '36': 3091, '37': 3400, '38': 3740, '39': 4114, '40': 4526, '41': 4979, '42': 5476, '43': 6024, '44': 6626, '45': 7289, '46': 8018, '47': 8820, '48': 9702, '49': 10672,
              '50': 11739, '51': 12913, '52': 14204, '53': 15625, '54': 17187, '55': 18906, '56': 20797, '57': 22876, '58': 25164, '59': 27680, '60': 30448, '61': 33493, '62': 36842, '63': 40527, '64': 44579, '65': 49037, '66': 53941, '67': 59335, '68': 65268, '69': 71795, '70': 78975, '71': 86872, '72': 95559, '73': 105115, '74': 115627,
              '75': 127190, '76': 139908, '77': 153899, '78': 169289, '79': 186218, '80': 204840, '81': 225324, '82': 247856, '83': 272642, '84': 299906, '85': 329897, '86': 362887, '87': 399175, '88': 439093, '89': 483002, '90': 531302, '91': 584432, '92': 642876, '93': 707163, '94': 777880, '95': 855668, '96': 941234, '97': 1035358, '98': 1138894, '99': 1252783, '100': 1378061
              }

rpg_help = {'cmds':'commands: register, buy, item, potion, propose, attack, equip, rpgstats.<br/> use rpghelp commandhere for specific info',
            'buy':'item (amount), weapon (amount), potion (amount)',
            'register': 'register in a clan with base stats',
            'item': 'shop (list of items), mylist (list of owned items), info (info about the item)',
            'potion': 'drink (drink a potion), shop (list of potions), mylist (list of owned potions)',
            'weapon': 'shop (list of weapons close to your level), mylist (list of owned weapons)',
            'propose': 'to username (if you have the wedding rings item you may propose to another user), accept username (accept a users proposal of marriage)',
            'attack': 'username (attack a user with your equipped weapon. affected by stats and timeouts. some weapons use ammo',
            'equip': 'equip a specific weapon',
            'rpgstats': 'username (check a users status or your own with no user name)'
            }

def _rpghelp(x, user, uid, roomname, othervars):
    if x == '':
        ret = rpg_help['cmds']
    else:
        try:
            ret = rpg_help[x.lower()]
        except: ret =  'invalid'
    return ret
    
def _register(x, user, uid, roomname, othervars):
    if user not in rpg_players:
        _status = dict(critchance=0.07, health=110, level=1, attack_timeout=time.time(), exp=0, accuracy=0.75, marriage={}, effects={})
        _inventory = dict(weapons={'unarmed':['equipped', 1]}, potions={}, items={}, money=150)
        skills = dict()
        _clan = random.choice(clan_list)
        _dict = dict(status=_status, inventory=_inventory, clan=_clan)
        rpg_players[user] = json.dumps(_dict)
        calc_level(user)
        return 'registered in clan ' + _clan
    else:
        return 'you are already registered'

def _item(arg, user, uid, roomname, othervars):
    try:
        try:
            _dict = json.loads(rpg_players[user])
        except:
            return 'you are not registered yet'
        try: title = _dict['title'] + ', '
        except: title = ''
        try: arg, item = arg.split(' ',1)
        except: arg, item = arg, ''
        if arg == 'shop':
            i = ', '.join([i+': cost-'+item_dict[i].split()[-1] for i in item_dict])
            return i
        elif arg == 'mylist':
            if len([i for i in _dict['inventory']['items']]) > 0:
                i = title+'your items are: '+', '.join([i for i in _dict['inventory']['items']])
                return i
            else: return title+'you have no items'
        elif arg == 'info':
            _item = ' '.join(item_dict[item].split()[:-1])
            return item+': '+_item
    except: return 'invalid'

def _potion(arg, user, uid, roomname, othervars):
    try:
        _dict = json.loads(rpg_players[user])
    except:
        return 'you are not registered yet'
    try: title = _dict['title'] + ', '
    except: title = ''
    try: arg, item = arg.split(' ',1)
    except: pass
    if arg == 'drink':
        if _dict['inventory']['potions'][item] <= 0:
            return title+'you are out of that potion'
        else:
            _dict['inventory']['potions'][item] -= 1
            if _dict['inventory']['potions'][item] <= 0:
                del _dict['inventory']['potions'][item]
            info = potion_dict[item].split()
            effect = info[2]
            val = info [1]
            level = _dict['status']['level']
            if effect == 'health':
                amount = _dict['status']['health'] + int(val)
                _amount = max_health[str(level)]
                if amount > _amount:
                    _dict['status']['health'] = _amount
                else:
                    _dict['status']['health'] += int(val)
            else:
                _dict['status']['effects'][effect] = [time.time(), val]
            _dict['status']['exp'] += 5
            rpg_players[user] = json.dumps(_dict)
            calc_level(user)
            return title+'you drank: ['+item+' potion]'
    elif arg == 'shop':
        return ', '.join([i+': cost - '+potion_dict[i].split()[0] for i in potion_dict])
    elif arg == 'mylist':
        try: return ', '.join([i+': supply - '+_dict['inventory']['potions'][i] for i in _dict['inventory']['potions']])
        except: return 'no potions'
        
def _weapon(arg, user, uid, roomname, othervars):
    try:  _dict = json.loads(rpg_players[user])
    except: return 'you are not registered yet'
    try: arg, item = arg.split(' ',1)
    except: pass
    if arg == 'shop':
        level = _dict['status']['level']
        a = []
        b = []
        for i in weapon_dict:
            if weapon_dict[i].split()[-1] == 'ranged':
                a.append([weapon_dict[i].split()[3], [i, weapon_dict[i].split()[0], weapon_dict[i].split()[-1], weapon_dict[i].split()[3]]])
            elif weapon_dict[i].split()[-1] == 'mele':
                b.append([weapon_dict[i].split()[3], [i, weapon_dict[i].split()[0], weapon_dict[i].split()[-1], weapon_dict[i].split()[3]]])
        c = [int(i[0]) for i in a]
        d = [int(i[0]) for i in b]
        c.sort()
        d.sort()
        _closest = min(c, key=lambda x: abs(int(x)-level))
        closest = min(d, key=lambda x: abs(int(x)-level))
        _nim = list(set(c))
        nim = list(set(d))
        _nim.sort()
        nim.sort()
        try: e = [c[c.index(_closest)], _nim[_nim.index(_closest)+1]]
        except: e = [c[c.index(_closest)]]
        try: f = [d[d.index(closest)], nim[nim.index(closest)+1]]
        except: f = [d[d.index(closest)]]
        g = []
        for i in e:
            for z in a:
                if int(z[0]) == int(i):                    
                    g.append(z[1])
        h = []
        for i in f:
            for z in b:
                if int(z[0]) == int(i):
                    h.append(z[1])
        return "<font color='#00ffff'>[</font>"+', '.join(['<font color="#00ff00">'+i[0]+'</font>: cost-'+i[1]+' type-'+i[2]+' level-'+i[3] for i in g])+"<font color='#00ffff'>]</font>, "+"<font color='#00ffff'>[</font>"+', '.join(['<font color="#00ff00">'+i[0]+'</font>: cost-'+i[1]+' type-'+i[2]+' level-'+i[3] for i in h])+"<font color='#00ffff'>]</font>"
    elif arg == 'mylist':
        derp = []
        for i in _dict['inventory']['weapons']:
            n = '['
            n+= i+' - '+_dict['inventory']['weapons'][i][0]
            if weapon_dict[i].split()[6] == 'ranged':
                n += ': ammo-'+str(_dict['inventory']['weapons'][i][1])
            n += ']'
            derp.append(n)
        return ', '.join(derp)
                    
def _attack(user, _user, uid, roomname, othervars):
    try: __dict = json.loads(rpg_players[_user])
    except: return 'you are not registered yet'
    try:  _dict = json.loads(rpg_players[user])
    except: return 'they are not registered yet'
    try: _title = __dict['title']+ ', '
    except: _title = ''
    try: title = _dict['title']
    except: title = user
    if __dict['status']['health'] < 1:
        return _title+'you are dead. you cannot attack'
    if _dict['status']['health'] < 1:
        return _title+tile+' is dead. you cannot attack'
    for i in __dict['inventory']['weapons']:
        _i = __dict['inventory']['weapons'][i]
        if _i[0] == 'equipped':
            weapon = i
            ammo = _i[1]
            break
    if ammo <= 0: return _title+'you are out of ammo'
    _stats = weapon_dict[weapon].split()
    base_damage = int(_stats[1])
    attack_rate = float(_stats[2])*5
    wtype = _stats[6]
    if attack_rate > 10000: attack_rate = 10000
    timeout = time.time() - __dict['status']['attack_timeout']
    if timeout < attack_rate:
        return _title+'you find yourself unable to attack fast enough [%s seconds]' % str(round(attack_rate -  timeout))
    needs_ammo = _stats[4]
    max_damage = base_damage * 3.5
    accuracy = __dict['status']['accuracy']
    critchance = __dict['status']['critchance']
    try:
        _critchance = __dict['status']['effects']['critchance']
        _timeout = _critchance[0]
        _timeout = time.time() - _timeout
        if _timeout > 600:
            del __dict['status']['effects']['critchance']
        else:
            critchance += round(float(_critchance[1]), 1)
    except: pass
    try:
        _accuracy = __dict['status']['effects']['accuracy']
        _timeout = _accuracy[0]
        _timeout = time.time() - _timeout
        if _timeout > 600:
            del __dict['status']['effects']['accuracy']
        else:
            accuracy += round(float(_accuracy[1]), 1)
    except: pass
    try:
        _invisibility, val = _dict['status']['effects']['invisibility']
        _timeout = _invisibility
        _timeout = time.time() - _timeout
        if _timeout > 600:
            del __dict['status']['effects']['invisibility']
        else:
            accuracy -= 0.35
    except: pass
    crit = False
    killed = False
    def hit_chance(i):
        part = round(i * 10000)
        _part = 10000 - part
        part = ['y' for i in range(int(part))]
        _part = ['n' for i in range(int(_part))]
        part = part + _part
        hit = random.choice(part)
        return hit
    if wtype == 'ranged':
        equipped ,_nyaaa = __dict['inventory']['weapons'][weapon]
        _nyaaa -= 1
        if _nyaaa <= 0: _nyaaa = 0
        __dict['inventory']['weapons'][weapon] = [equipped, _nyaaa]
    if hit_chance(accuracy) == 'n':
        __dict['status']['attack_timeout'] = time.time()
        rpg_players[_user] = json.dumps(__dict)
        rpg_players[user] = json.dumps(_dict)
        calc_level(_user)
        return _title+'you missed!!!'
    if hit_chance(critchance) == 'y':
        crit = True
        max_damage *= 2       
    min_damage = max_damage * 0.6
    damage = random.randrange(round(min_damage), round(max_damage))
    _dict['status']['health'] -= damage
    level = _dict['status']['level']
    _level = __dict['status']['level']
    _kexp = round(max_health[str(level)]/random.choice([12,11,13]))
    _exp = round(max_health[str(_level)]/random.choice(range(20,35))) 
    if _dict['status']['health'] <= 0:
        _dict['status']['health'] = 0
        killed = True
        __dict['status']['exp'] += _kexp
        __dict['inventory']['money'] += _kexp
    __dict['inventory']['money'] += _exp
    __dict['status']['exp'] += _exp
    __dict['status']['attack_timeout'] = time.time()        
    rpg_players[user] = json.dumps(_dict)
    rpg_players[_user] = json.dumps(__dict)
    calc_level(_user)
    ret = _title+'you attacked ' + title + ' for ' + str(damage)+' damage. their health: '+ str(_dict['status']['health'])
    if crit == True: ret = ret + ': critical hit!!!'
    if killed == True: ret = ret + ': '+title+' was killed'
    return ret

def calc_level(user):
    _dict = json.loads(rpg_players[user])
    exp = _dict['status']['exp']
    _exp = max_health[str(_dict['status']['level'])]
    while True:
        if exp > _exp:
            _left = exp - _exp
            _dict = json.loads(rpg_players[user])
            _exp = max_health[str(_dict['status']['level'])]
            exp -= _exp
            _dict['status']['exp'] = _left
            if _dict['status']['level'] >= 100:
                _dict['status']['level'] = 100
            else:
                _dict['status']['level'] += 1
            level = _dict['status']['level']
            _health = max_health[str(level)]
            _dict['status']['health'] = _health
            if _dict['status']['accuracy'] >= 1:
                _dict['status']['accuracy'] = 1
            else: _dict['status']['accuracy'] += 0.0025
            rpg_players[user] = json.dumps(_dict)
        else: break
    dumprpg()

def _propose(arg, _user, uid, roomname, othervars):
    try:
        arg, user = arg.split()
        _dict = json.loads(rpg_players[user])
        __dict = json.loads(rpg_players[_user])
        try: _title = __dict['title']+ ', '
        except: _title = ''
        try: title = _dict['title']
        except: title = user
        if arg == 'to':
            proposed = []
            try:
                _ret = _dict['status']['marriage']['proposed']
                proposed += _ret
            except:
                pass
            try:
                ret = _dict['status']['marriage']['married']
                try: ret = rpg_players[ret]['title']
                except: ret = ret
                return  title+'is already married to ' + ret
            except:
                __dict['inventory']['items']['wedding rings']
                proposed.append(_user)
                _dict['status']['marriage']['proposed'] = list(set(proposed))
                try:
                    ret = __dict['status']['marriage']['proposing']
                    try: ret = rpg_players[ret]['title']
                    except: ret = ret
                    return _title+'you are already proposing to ' + ret
                except:
                    __dict['status']['marriage']['proposing'] = user
                    rpg_players[user] = json.dumps(_dict)
                    rpg_players[_user] = json.dumps(__dict)
                    calc_level(_user)
                    return _title+'you have proposed to ' + title
        if arg == 'accept':
            ret = __dict['status']['marriage']['proposed']
            if user in ret:
                __dict['inventory']['items']['wedding rings'] = 'given'
                try: del __dict['status']['marriage']['proposed']           
                except: pass
                try: del _dict['status']['marriage']['proposed']
                except: pass
                try: del __dict['status']['marriage']['proposing']
                except: pass
                try: del _dict['status']['marriage']['proposing']
                except: pass
                for i in rpg_players:
                    derp = json.loads(rpg_players[i])
                    try:
                       if user in derp['status']['marriage']['proposed']:
                           derp['status']['marriage']['proposed'].remove(user)
                    except:
                        pass
                    try:
                        if _user in derp['status']['marriage']['proposed']:
                           derp['status']['marriage']['proposed'].remove(_user)
                    except:
                        pass
                    try:
                        if derp['status']['marriage']['proposing'] == user or _user:
                           del derp['status']['marriage']['proposing']
                    except:
                        pass
                    rpg_players[i] = json.dumps(derp)
                _dict['status']['marriage']['married'] =  _user
                __dict['status']['marriage']['married'] = user
                _dict['status']['exp'] += 5000
                __dict['status']['exp'] += 5000
                rpg_players[user] = json.dumps(_dict)
                rpg_players[_user] = json.dumps(__dict)
                calc_level(_user)
                calc_level(user)
                return _title+'you are now married to ' + title
            else: return title+' has not proposed to you'
    except:
        return 'not vallid'

def _rpgstats(user, _user, uid, roomname, othervars):
    user = _user if user == '' else user.lower()
    try:
        rpg_players[user]
    except:
        return 'you/they are not registered yet'
    _dict = json.loads(rpg_players[user])
    rel = _dict['status']['marriage']
    try: _title_ = _dict['title']
    except: _title_ = user
    try:
        proposed_to = rel['proposed']
        _i = []
        for i in proposed_to:
            try: title = json.loads(rpg_players[i])['title']
            except: title = i
            _i.append(title)
        _rel = 'proposed to by: ' + ', '.join(_i)
    except:
        _rel = ''
    try:
        married_to = rel['married']
        try: _title = _dict['title']
        except: _title = married_to
        rel = 'married to: ' + _title
    except: rel = 'not married'
    level = str(_dict['status']['level'])
    exp = str(_dict['status']['exp'])
    health = str(_dict['status']['health'])
    clan = _dict['clan']
    money = _dict['inventory']['money']
    if _rel == '': derp = ['name: '+_title_, rel, 'exp: ' + exp, 'level: '+level, 'health: '+health, 'clan: '+clan, 'money: '+str(money)]
    else: derp = ['name: '+_title_, rel, _rel, 'exp: ' + exp, 'level: '+level, 'health: '+health, 'clan: '+clan, 'money: '+str(money)]
    return '<br/><br/><br/>' + '<br/>'.join(derp)
    

def _equip(weapon, user, uid, roomname, othervars):
    try:
        rpg_players[user]
    except:
        return 'you are not registered yet'
    _dict = json.loads(rpg_players[user])
    try: _title = _dict['title'] + ', '
    except: _title = ''
    try:
        for i in _dict['inventory']['weapons']:
            if _dict['inventory']['weapons'][i][0] == 'equipped':
                ammo = _dict['inventory']['weapons'][i][1]
                _dict['inventory']['weapons'][i] = ['unequipped', ammo]
        ammo = _dict['inventory']['weapons'][weapon][1]
        _dict['inventory']['weapons'][weapon] = ['equipped', ammo]
        _dict['status']['exp'] += 5
        rpg_players[user] = json.dumps(_dict)
        calc_level(user)
        return _title+'equipped ' + weapon
    except:
        return _title+'you do not have that weapon'

def _buy(arg, user, uid, roomname, othervars):
    try:
        rpg_players[user]
    except:
        return 'you are not registered yet'
    arg, item = arg.split(' ',1)
    _item = item.split()
    try:
        amount = int(_item[-1]) 
        _item.remove(_item[-1])
    except: amount = 1
    if amount < 1: return 'amount must be greater than 0'
    _name = ' '.join(_item)
    _dict = json.loads(rpg_players[user])
    money = _dict['inventory']['money']
    level = _dict['status']['level']
    try: _title = _dict['title'] + ', '
    except: _title = ''
    if arg == 'weapon':
        i = weapon_dict[_name].split()
        cost = int(i[0])
        need_ammo = i[4]
        ammo = int(i[5])
        if need_ammo == 'yes':
            ammo *= amount        
        _level = int(i[3])
        if _level > level:
            return _title+'your level is not high enough'
        cost *= amount
        if money >= cost:
            money -= cost
        else:
            return _title+'you do not have enough money'
        _dict['inventory']['weapons'][_name] = ['unequipped', ammo]
    elif arg == 'item':
        i = item_dict[_name].split()
        cost = int(i[-1])
        cost *= amount
        if money >= cost:
            money -= cost
        else:
            return _title+'you do not have enough money'
        if _name == 'royal crest':
            _gender = gender(user)
            if _gender == 'him': title = 'lord '+user
            elif _gender == 'her': title = 'lady '+user
            elif _gender == 'them': title = 'your grace: '+user
            _dict['title'] = title
        _dict['inventory']['items'][_name] = 'purchased'
    elif arg == 'potion':
        i = potion_dict[_name].split()
        cost = int(i[0])
        cost *= amount
        if money >= cost:
            money -= cost
        else:
            return _title+'you do not have enough money'
        try: _dict['inventory']['potions'][_name] += amount
        except: _dict['inventory']['potions'][_name] = amount
    elif arg == 'ammo':
        i = weapon_dict[_name].split()
        need_ammo = i[4]
        if need_ammo == 'yes':
            if _name == 'nuke':
                cost = int(i[0])
                _amount = 1
            else:
                cost = int(i[0])/10
                _amount = 10
            cost *= amount
            amount *= _amount
            if money >= cost:
                money -= cost
            else:
                return _title+'you do not have enough money'
            try:
                equipped, pammo = _dict['inventory']['weapons'][_name]
                pammo += amount
                _dict['inventory']['weapons'][_name] = [equipped, pammo]
            except: return 'you dont have that weapon'            
    _dict['inventory']['money'] = money    
    _dict['status']['exp'] += 3*level
    rpg_players[user] = json.dumps(_dict)
    calc_level(user)
    try: _title = _dict['title'] + ', ' 
    except: _title = ''
    return _title+'you bought ' + str(amount) + ' ' + _name + ' '+ arg + ' for ' + str(cost) + ' gold'

def dumprpg():
    f = open("rpg.txt", "w")
    for i in rpg_players:
           _dict = json.loads(rpg_players[i])
           f.write(json.dumps([i,_dict])+"\n")                                        
    f.close()

def _mail(x, user, uid, roomname, othervars):
    try:
            mid = str(random.randrange(10000, 99999))
            name, message = x.split(' ',1)
            name = name.lower()
            stime = time.time()
            if len(message) == 0: return 'fail'
            message = escape(message)
            rmind[mid] = json.dumps([name, message, user, stime])
            _notify(name)
            f = open("rmind.txt", "w")
            for i in rmind:
                name, msg, _user, stime = json.loads(rmind[i])                                        
                f.write(json.dumps([i, name, msg, _user, stime])+"\n")
            f.close()
            return "I will mail %s that." % gender(name)
    except Exception as e:
            return 'fail'

def _inbox(x, user, uid, roomname, othervars):
    try:
        y = []
        n = []
        for i in rmind:
            name, msg, _user, stime = json.loads(rmind[i])
            n.append(i)
            if user == name:
                y.append('Message from %s to %s: %s - sent %s ago.' % (_user, name, msg, getSTime(float(stime))))
        for i in n:
            del rmind[i]
        f = open("rmind.txt", "w")
        for i in rmind:
                _name, _msg, __user, _stime = json.loads(rmind[i])                                        
                f.write(json.dumps([i, _name, _msg, __user, _stime])+"\n")
        f.close()
        return '<br/><br/>'+'<br/>'.join(y) if len(y) > 0 else 'no message yet!!'
    except Exception as e : return print(e)

def _yt(vid, user, uid, roomname, othervars):
    banned = vid.split()
    if bool(set(banned) & set(banned_terms)):
        return 'no u'
    vid = urllib.parse.quote(vid.replace(" ", "+"))
    _url = ("https://www.googleapis.com/youtube/v3/search?q=/%s&part=snippet&key=%s") % (vid, api_key)
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
        return '[%s]<br/>%s' % (title, link)
    else:
        return 'no results'

def _gws(x, user, uid, roomname, othervars):
    try:
        banned = x.split()
        if bool(set(banned) & set(banned_terms)):
            return 'no u'
        x = urllib.parse.quote(x.replace(" ", "+"))
        _url = ('https://www.googleapis.com/customsearch/v1?key=%s&cx=fbd2fe34e5392ec2a&safe=off&q=%s' % (api_key, x))
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

def _gis(x, user, uid, roomname, othervars):
    banned = x.split()
    if bool(set(banned) & set(banned_terms)):
        return 'no u'
    x = urllib.parse.quote(x.replace(" ", "+"))
    _url = ('https://www.googleapis.com/customsearch/v1?key=%s&cx=e4944556d694be885&safe=off&num=10&searchType=image&q=%s' % (api_key, x))
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

def _tran(x, user, uid, roomname, othervars):
    x = x.lower()
    try:
        banned = x.split()
        if bool(set(banned) & set(banned_terms)):
            return 'no u'
        dest, _text = x.split(' ',1)
        if dest in lang.keys():
            dest = lang[dest]
        if dest not in lang.values():
            return 'Invalid language. use langs command to see available languages'
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

def expired_time(x):
    total_seconds = float(time.time() - x)
    if total_seconds >= 8640000: return 'already expired'
    total_seconds = 8640000 -  total_seconds
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
    return string + ' left'

def _expires(x, user, uid, chat, othervars):
    x = x.lower()
    try:
        othervars[1].ustatus[b][0]
    except:
        othervars[1].friend_add(x)
    def expires(b):
        time.sleep(2)
        try:
            _time = othervars[1].ustatus[b][0]
            _time = expired_time(float(_time))
            chat.post(b+': '+_time)
            othervars[1].unfriend(b)
        except:
            chat.post('invalid, try again and check spelling')
    _task(expires, x)
    return 'working on it. give the bot 4 seconds to respond before trying again'

def name_color_gen():
    clist, i, color = ['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'], 0, []
    while (i < 6): color.append(random.choice(clist)); i+=1
    return ''.join(color)

def _whois(x, user, uid, roomname, othervars): 
    return ', '.join(roomname.whois(x.lower()))

def _delwhois(x, user, uid, roomname, othervars):
    return roomname.delwhois(x.lower())

def dumpwhois(x):
    print('saving')
    time.sleep(3)
    f = open("whois.txt", "w")
    for i in cakelib2.uids:
           _uid = json.loads(cakelib2.uids[i])
           f.write(json.dumps([i, _uid])+"\n")                                        
    f.close()
    f = open("lastmsg.txt", "w")
    for i in lastmsg:
        msg, room, seentime = json.loads(lastmsg[i])
        f.write(json.dumps([i, msg, room, seentime])+"\n")
    f.close()
    print('saving done')

def _post(x, user, uid, roomname, othervars):
    try:
            keylist = list('12345678910@$&*^#!abcdefghijklmnopqrstuvwxyz')
            key = ''.join([random.choice(keylist) for x in range(6)])
    except Exception as e: print(e)
    if len(x) == 0: return 'fail'
    if len(__board.keys()) > 5:
        __board.clear()
    x = escape(x)
    x = '%s - <font color="#00ffff"><b>%s</b></font>: %s' % (time.strftime('%c'), user, x)
    __board[key] = json.dumps(x)
    f = open("board.txt", "w")
    for i in __board:
           _post = json.loads(__board[i])
           f.write(json.dumps([i, _post])+"\n")                                        
    f.close()
    return 'Posted to the board.'

def _board(x, user, uid, roomname, othervars):
    y = [json.loads(__board[x]) for x in __board]
    return '<br/><br/>'+ '<br/>'.join(y)

def gender(x):
    x = x.lower()
    try: resp = urllib.request.urlopen("http://st.chatango.com/profileimg/%s/%s/%s/mod1.xml" % (x[0], x[1], x))
    except: resp = urllib.request.urlopen("http://st.chatango.com/profileimg/%s/%s/%s/mod1.xml" % (x[0], x[0], x))
    try: data = resp.read().decode()
    except: data = resp.read().decode('latin-1')
    try: ru = re.compile(r'<s>(.*?)</s>', re.IGNORECASE).search(data).group(1)
    except: ru = "?"
    ret = urllib.parse.unquote(ru)
    if ret == "M": r = "him"
    elif ret == "F": r = "her"
    elif ret == "?": r = "them"        
    return r

def _bgtime(x, user, uid, chat, cake):
    x = x.lower() if len(x) > 0 else user
    try: resp = opener.open("https://st.chatango.com/profileimg/%s/%s/%s/mod1.xml" % (x[0], x[1], x))
    except: resp = opener.open("https://st.chatango.com/profileimg/%s/%s/%s/mod1.xml" % (x[0], x[0], x))
    try: data = resp.read().decode()
    except: data = resp.read().decode('latin-1')
    resp.close()
    try: data = re.compile(r'<d>(.*?)</d>', re.IGNORECASE).search(data).group(1)
    except: return 'they have never had a background, or that is not a real user'
    data = int(data)
    if data < time.time(): return 'that users background expired: ' + getSTime(data) + ' ago'
    else:
        return 'that user has: ' + getBGTime(data) + ' left'

def is_online(user):
    resp = urllib.request.urlopen("http://"+user+".chatango.com").read().decode()
    return str(bool('chat with' in resp.lower()))+ ' '+user

def _cmds(x, user, uid, chat, cake):
    return 'in progress -- for now: [rpghelp, whois, pfp, msbg, seen, bgtime, yt, gis, gws, tran, mail, inbox show/check, owner, post, board]' 

chatderp = []
chatobj = []

def _owner(x, user, uid, chat, cake):
    x = x.lower()
    if cakelib2.checkG(x) == True:
        try:
            owner = cake[2].gChat(x).chatInfo.owner
        except:
            cake[2].joinChat(x)
        chatderp.append('i')
        def _owner(b):
            time.sleep(2)
            owner = cake[2].gChat(x).chatInfo.owner
            chatobj.append(cake[2].gChat(x))
            chatderp.remove('i')
            chat.post('the owner is: ' + owner)
        _task(_owner, x)
        return 'working on it. give the bot 4 seconds to respond before trying again'
    else: return 'that is not a real chat name'
    
def _rmanage(x, user, uid, chat, cake):
    x = x.lower()
    if len(x.split(' ')) > 1:
        x = x.split(' ')
        func, _room = x[0], x[1]
    else:
        func = x        
    if cake[3].rank < 2 and func != 'list': return 'You do not have moderator permissions.'
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
    
def _mod(x, user, uid, roomname, othervars):
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
            else: return 'derp'
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

