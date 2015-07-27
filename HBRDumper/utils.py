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
    def __init__(self, ID, name, country, admin):
        self.ID = ID
        self.name = name
        self.country = country
        self.admin = admin
        self.pings = []
        
    def average_ping(self):
        return "{:.02f}".format(sum(self.pings) / len(self.pings))
        
    def __repr__(self):
        return 'Player(ID={s.ID}, name={s.name}, country={s.country}, admin={s.admin})'.format(s=self)
        
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
        
__ALL__ = ['Action', 'Player', 'find_by_attr', 'format_time']