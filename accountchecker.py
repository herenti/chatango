import urllib.request
import urllib.parse
import json
import random
import re
import time
import socket

_d = list()
f = open('words.txt', 'r')
for line in f.readlines():
        try:
                if len(line) > 0:
                        _d.append(line.strip().lower()) 
        except Exception as e:
                print("Could not load words: %s" % e)
f.close()

a = [i for i in _d if i.startswith('a')]
b = [i for i in _d if i.startswith('b')]
c = [i for i in _d if i.startswith('c')]
d = [i for i in _d if i.startswith('d')]
e = [i for i in _d if i.startswith('e')]
f = [i for i in _d if i.startswith('f')]
g = [i for i in _d if i.startswith('g')]
h = [i for i in _d if i.startswith('h')]
i = [i for i in _d if i.startswith('i')]
j = [i for i in _d if i.startswith('j')]
k = [i for i in _d if i.startswith('k')]
l = [i for i in _d if i.startswith('l')]
m = [i for i in _d if i.startswith('m')]
n = [i for i in _d if i.startswith('n')]
o = [i for i in _d if i.startswith('o')]
p = [i for i in _d if i.startswith('p')]
q = [i for i in _d if i.startswith('q')]
r = [i for i in _d if i.startswith('r')]
s = [i for i in _d if i.startswith('s')]
t = [i for i in _d if i.startswith('t')]
u = [i for i in _d if i.startswith('u')]
v = [i for i in _d if i.startswith('v')]
w = [i for i in _d if i.startswith('w')]
x = [i for i in _d if i.startswith('x')]
y = [i for i in _d if i.startswith('y')]
z = [i for i in _d if i.startswith('z')]

def regex(pattern, _x, default): return re.search(pattern, _x).group(1) if re.search(pattern, _x) else default

def _login(_u, _p):
    data = urllib.parse.urlencode({"user_id": _u, "password": _p, "storecookie": "on", "checkerrors": "yes"}).encode()
    ret = regex('auth.chatango.com=(.*?);', urllib.request.urlopen("http://chatango.com/login", data).getheader('Set-Cookie'), '')
    if ret != '':
        cumsock = socket.socket()
        cumsock.connect(('c1.chatango.com', 5222))
        cumsock.send(('tlogin:'+ret+':2\x00').encode())
        time.sleep(0.3)
        for _i in b: #do a-z one at a time or _d all at once.
                cumsock.send(('wladd:'+_i+'\r\n\x00').encode())
                time.sleep(0.3)
        cumsock.close()
        print('done')
    return
