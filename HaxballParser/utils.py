import time

class Message:
    def  __init__(self, name, inprog, msg):
        self.name = name
        self.in_progress = inprog
        self.msg = msg

    def __repr__(self):
        return 'Message(name={s.name}, in_progress={s.in_progress}, msg={s.msg})'.format(s=self)

    def __str__(self):
        return 'Said: ' + self.msg

class Action:
    def __init__(self, time, senderID, action, parsed):
        self.time = time
        self.senderID = senderID
        self.action = action
        self.parsed = parsed
        
    def __repr__(self):
        return 'Action(time={s.time}, senderID={s.senderID}, action={s.action}, parsed={s.parsed})'.format(s=self)

class PlayerHandler:
    def __init__(self, actionparser):
        self.ap = actionparser
        self.players = self.ap.result['Players']
        self.player_bin = []

    def update_pings(self, pings):
        [self.players[p].pings.append(pings[p]) for p in range(len(pings))]

    def start_pt(self):
        [p.start_pt(self.ap.cframe) for p in self.players]

    def stop_pt(self):
        [p.stop_pt(self.ap.cframe) for p in self.players]

    def add_player(self, p):
        self.players.append(p)

    def remove_player(self, pid):
        p = self.get_from_id(pid)
        p.removed = True
        self.player_bin.append(p)
        del self.players[self.players.index(p)]

    def move_player(self, p, team):
        p.team = team
        if self.ap.in_progress:
            p.start_pt(self.ap.cframe)
            if team == 'Spectator':
                p.stop_pt(self.ap.cframe)

        # Move player to the back of the list
        idx = self.players.index(p)
        self.players.pop(idx)
        self.players.append(p)

    def get_from_id(self, pid):
        return find_by_attr_val(self.players, {'ID':pid})
        
class Player:
    def __init__(self, ID, name, country, admin, team, avatar, orig=True):
        self.ID = ID
        self.name = name
        self.country = country
        self.admin = admin
        self.team = team
        self.avatar = avatar

        self.frames_in = 0
        self.orig = orig == True
        self.removed = False
        self.last_cframe = None
        self.pings = []
        
    @property
    def seconds(self):
        return self.frames_in / 60

    @property
    def pt(self):
        return format_time(self.seconds)

    def start_pt(self, cf):
        if self.team != 'Spectator':
            self.last_cframe = cf

    def stop_pt(self, cf):
        if self.last_cframe is not None:
            self.frames_in += cf - self.last_cframe
            self.last_cframe = None

    def average_ping(self):
        # Remove all 0s from pings
        p = [p for p in self.pings if p > 0]

        if len(p) > 0:
            return int(sum(p) / len(p))
        else:
            return 0
        
    def __repr__(self):
        return 'Player(ID={s.ID}, name={s.name}, country={s.country}, team={s.team}, admin={s.admin}, avatar={s.avatar}, pt={s.pt}, ping={ap})'.format(s=self, ap=str(self.average_ping()))
        
def find_by_attr_val(lst, attrs, multiple=False):
    res = []
    for a in lst:
        if all(getattr(a, attr) == attrs[attr] for attr in attrs.keys()):
            if multiple:
                res.append(a)
            else:
                return a
    return res

def format_time(s):
    return time.strftime("%H:%M:%S", time.gmtime(s))
        
class ParserError(Exception):
    def __init__(self, reason):
        self.reason = reason
        
    def __repl__(self):
        return self.reason
        
    def __str__(self):
        return repl(self)
        
__ALL__ = ['PlayerHandler', 'Message', 'Action', 'Player', 'ParserError', 'find_by_attr_val', 'format_time']