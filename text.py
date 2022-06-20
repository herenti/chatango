import json
import cakelib2

_board = dict()
f = open('board.txt', 'r')
print('Loading board...')
for line in f.readlines():
        try:
                if len(line) > 0:
                        key, post = json.loads(line.strip())
                        _board[key] = json.dumps(post)        
        except Exception as e:
                print("Could not load board: %s" % e)
f.close()

f = open('whois.txt', 'r')
print('Loading whois...')
for line in f.readlines():
        try:
                if len(line) > 0:
                        _uid, _names = json.loads(line.strip())
                        cakelib2.uids[_uid] = json.dumps(_names)        
        except Exception as e:
                print("Could not load whois: %s" % e)
f.close()

rpg_players = dict()
f = open('rpg.txt', 'r')
print('Loading rpg...')
for line in f.readlines():
        try:
                if len(line) > 0:
                        user, _dict = json.loads(line.strip())
                        rpg_players[user] = json.dumps(_dict)        
        except Exception as e:
                print("Could not load rpg: %s" % e)
f.close()

_mods = list()
f = open('mods.txt', 'r')
print('Loading mods...')
for line in f.readlines():
        try:
                if len(line) > 0:
                        _mods.append(line.strip())       
        except Exception as e:
                print("Could not load Mods: %s" % e)
f.close()

jsonrooms = dict()
room_list = []
lockrooms = []
f = open("jsonrooms.txt", "r")
print("Loading jsonrooms...")
for line in f.readlines():
        if len(line.strip()) > 0:
                roomname, joiner, roomlock, jointime, locker, locktime = json.loads(line.strip())
                jsonrooms[roomname] = json.dumps([joiner, roomlock, jointime, locker, locktime])
                if roomname not in room_list:
                        room_list.append(roomname.strip())
                else:
                        continue
                if roomlock == "True":
                        lockrooms.append(roomname.strip())
                else:
                        continue
f.close()

notify = dict()
f = open("notify.txt", "r")
print('Loading notify...')
for line in f.readlines():
        try:
                if len(line.strip()) > 0:
                        user, message  = json.loads(line.strip())
                        notify[user] = json.dumps(message)
        except Exception as e:
                print("Could not load notify: %s :%s" % (line, e))
f.close()

rmind = dict()
f = open("rmind.txt", "r")
print('Loading rmind...')
for line in f.readlines():
        try:
                if len(line.strip()) > 0:
                        mid, name, msg, user, stime  = json.loads(line.strip())
                        rmind[mid] = json.dumps([name, msg, user, stime])
        except:
                print("Could not load rmind: %s" % line)
f.close()
