import re
import urllib.request
import urllib.parse
import time

#modified from Vissle Drissle's program

'''MIT License

Copyright (c) 2023 Vissle Drissle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

def regex(pattern, x, default): return re.search(pattern, x).group(1) if re.search(pattern, x) else default

headers = {
  "User-Agent": "Mozilla/5.0"
  }

def updateprofile():
    user_id = input ('username: ')
    _password = input ('password: ')
    link = "https://chatango.com/updateprofile?css"
    data = {
        "s": Auth(user_id, _password),
        "auth": "token",
        "arch": "h5",
        "src": "group",
        "action": "update"
    }
    form = {}
    form["body_bg_col"] = input('background html code: ')
    form["body_col"] = input('text html code: ')
    form["body_a_col"] = input('link html code: ')
    form["body_tile_a"] = 0
    form["body_tile_d"] = 0
    payload = data | form
    payload = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(link, payload, headers=headers)
    update = urllib.request.urlopen(req)
    print('done. next account:')
    time.sleep(0.5)
    return 
    
def Auth(user, password): 
    data = urllib.parse.urlencode({"user_id": user, "password": password, "storecookie": "on", "checkerrors": "yes"}).encode()
    return regex('auth.chatango.com=(.*?);', urllib.request.urlopen("http://chatango.com/login", data).getheader('Set-Cookie'), None)

while True:
    updateprofile()
