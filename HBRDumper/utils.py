import time

class Action:
    def __init__(self, time, senderID, action, parsed):
        self.time = time
        self.senderID = senderID
        self.action = action
        self.parsed = parsed
        
    def __repr__(self):
        return 'Action(time={s.time}, senderID={s.senderID}, action={s.action}, parsed={s.parsed})'.format(s=self)
    
class Player:
    def __init__(self, ID, name, country, admin, team, avatar):
        self.ID = ID
        self.name = name
        self.country = country
        self.admin = admin
        self.team = team
        self.avatar = avatar
        self.pings = []
        
    def average_ping(self):
        return "{:.02f}".format(sum(self.pings) / len(self.pings))
        
    def __repr__(self):
        return 'Player(ID={s.ID}, name={s.name}, country={s.country}, team={s.team}, admin={s.admin})'.format(s=self)
        
def find_by_attr_val(lst, attr, val, multiple=False):
    res = []
    for a in lst:
        if getattr(a, attr) == val:
            if multiple:
                res.append(a)
            else:
                return a
            
    return res if len(res)>0 else None

def format_time(ms):
    return time.strftime("%H:%M:%S", time.gmtime(ms))
        
class ParserError(Exception):
    def __init__(self, reason):
        self.reason = reason
        
    def __repl__(self):
        return self.reason
        
    def __str__(self):
        return repl(self)
        
__ALL__ = ['Action', 'Player', 'ParserError', 'find_by_attr_val', 'format_time']