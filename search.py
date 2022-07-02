
uids = {'23393105': ['te4','te5'],'26419005': ['te3','te4'],'23983780': ['te2','te3'],'23390465': ['te2','te1'],'23386205': ['voxela','muse','te1'], '34166780': ['slug', 'muse', 'pixie', 'cunn', 'zombie', 'opal', 'virgo', 'charm', 'skann', 'feline', 'crush', 'rune', 'ejae', 'squirtle', 'succubi', 'hex', 'halo', 'horo'], '86298963': ['xxkaringtonxx'], '56157642': ['h'], '98904156': ['kenyan'], '48833405': ['atticus'], '85707971': ['agentpaper'], '66931466': ['sapphire', 'hershey'], '87888214': ['thorasic'], '10917657': ['lethebot'], '62797501': ['asriel'], '88081233': ['trav', 'trantran122', 'tasty', 't', 'raccoon', 'tea'], '11136664': ['jessicanigrifanclub', 'courtney'], '16631726': ['heartbeat'], '27002630': ['ainzsyn']
    }


def rUids(k, v):
    #on all relavant chatango room events pass uid/username to this function. g_participants, participant, i, b any others
    key, value = k.lower(), v.lower()    
    if key not in uids:
        uids[key] = [value]
    else:
        x = []
        values = uids[key]
        x += values
        x.append(value)
        x = list(set(x))
        uids[key] = x

def _whois(string):
    a = []
    for i in uids:
        i = uids[i]
        if string in i:
            a += i
    return list(set(a))

def whois(string):
    a = [string]
    while True:
        l = len(a)
        for n in a:
            i = _whois(n)
            if len(i) > 0: a += i
            else: a = ['no accounts for that user']; break
            a = list(set(a))
        if l == len(a):
            break
    return sorted(a)

def delwhois(string):
    string = string.split()
    for x in string:
        for i in uids:
            n = uids[i]
            if x in n:
                n.remove(x)
                uids[i] = n
    return


print(', '.join(whois('zombie')))
