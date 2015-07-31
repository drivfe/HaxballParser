from .parser import Parser
from .utils import *

class ActionParser(Parser):
    def __init__(self, btsio, players):
        super().__init__(btsio)
        self.players = players
        self.player_bin = []
        self.rem_data_size = len(btsio)
        self.replaytime = 0
        self.cur_senderID = 0
        self.actions = [
            'newPlayer',
			'removePlayer',
			'playerChat',
			'logicUpdate',
			'startMatch',
			'stopMatch',
			'discMove',
			'changeTeam',
			'changeTeamsLock',
			'changeGameSettings',
			'changePlayerAvatar',
			'announceDesync',
			'changePlayerAdminRights',
			'changeStadium',
			'pauseGame',
			'broadcastPing',
			'announceHandicap'
        ]

    def move_player(self, p, team):
        p.team = team

        # Move player to the back of the list
        idx = self.players.index(p)
        self.players.pop(idx)
        self.players.append(p)

    def del_player(self, id):
        try:
            p = find_by_attr_val(self.players, {'ID': id})
            if p:
                p.removed = True
                self.player_bin.append(p)
                del self.players[self.players.index(p)]
        except KeyError:
            pass
        
    def player(self, id):
        sender = find_by_attr_val(self.players, {'ID': id})
        return sender

    def dump(self):
        cframe = 0
        action_list = []
        action_ignore = ['discMove', 'broadcastPing']
        
        self.nxt(14) # I don't know what the first 14 bytes are.

        # Stuff to make parsing faster
        dnext = self.dump_next
        pos = self.pos
        alappend = action_list.append
        pb = self.parse_bool
        pu = self.parse_uint

        while pos() < self.rem_data_size:
            if pb(): # True if this is a different frame.
                cframe += pu()
                self.replaytime = cframe / 60
            
            action = dnext()

            if action.parsed != None and action.action not in action_ignore and action.senderID < 50:
                alappend(action)
        
        self.finished()

        return action_list
            
    def finished(self):
        # Merge players and player_bin
        [self.players.append(np) for np in self.player_bin]

        # Remove all 0s from pings
        for p in self.players:
            while p.pings.count(0) > 0:
                p.pings.remove(0)
 
    def dump_next(self):
        self.cur_senderID = self.parse_uint()
        action = self.actions[self.parse_byte()]
        parsed = getattr(self, action)()
        
        return Action(time=self.replaytime, senderID=self.cur_senderID, action=action, parsed=parsed)
        
    def announceHandicap(self):
        return 'Handicap set to '+ str(self.parse_ushort())
        
    def broadcastPing(self):
        num = self.parse_byte()
        
        # Ugly but faster
        [self.players[p].pings.append(self.parse_byte()*4) for p in range(num)]
            
        return 'Pings updated'
        
    def changeGameSettings(self):
        setting = self.parse_byte()
        val = self.parse_uint()
        
        return 'Settings changed'
        
    def changePlayerAdminRights(self):
        player = self.player(self.parse_uint())
        admin = self.parse_bool()
        player.admin = admin
        
        if not player:
            return None

        if not admin:
            return 'Removed admin from '+ player.name
        
        return 'Made '+ player.name +' an admin'
        
    def changePlayerAvatar(self):
        ava = self.parse_str()
        player = self.player(self.cur_senderID)
        if not player:
            return None
        player.avatar = ava
        return 'Avatar changed to: '+ ava
        
    def pauseGame(self):
        return 'Game ' + 'paused' if self.parse_bool() else 'unpaused'
        
    def changeStadium(self):
        len = self.parse_uint()
        
        return 'Map changed to ' + self.parse_stadium()
        
    def changeTeamsLock(self):
        return '{} teams'.format('Unlocked' if not self.parse_bool() else 'Locked')
        
    def changeTeam(self):
        player = self.player(self.parse_uint())
        team = self.parse_side()
        
        if not player:
            return None
            
        if team == player.team: # player was not moved, glitch.
            return None
        
        self.move_player(player, team)
        
        return 'Moved '+ player.name +' to '+ team
        
    def discMove(self):
        return self.parse_byte()
        
    def stopMatch(self):
        return 'Stopped match'
        
    def startMatch(self):
        return 'Started match'
    
    def logicUpdate(self):
        return 'Logic update'
    
    def playerChat(self):
        return 'Said: '+ self.parse_str()
        
    def newPlayer(self):
        ID = self.parse_uint()
        name = self.parse_str()
        admin = self.parse_bool()
        country = self.parse_str()
        p = Player(
                ID=ID,
                name=name,
                admin=admin,
                country=country,
                team='Spectator',
                avatar='',
                orig=False
            )
        self.players.append(p)
        
        return name+' joined'
        
    def removePlayer(self):
        ID = self.parse_ushort()
        player = self.player(ID)
        kicked = self.parse_bool()
        
        if kicked:
            reason = self.parse_str()
            
        ban = self.parse_bool()
        
        if not player:
            return None
            
        self.del_player(ID)
            
        if kicked:
            return '{} was {}: {}'.format(player.name, 'banned' if ban else 'kicked', reason)
        
        else:
            return '{} left'.format(player.name)
     
     
    def announceDesync(self):
        return 'Desynchronized'
