from collections import namedtuple
from .parser import Parser, Action, Player

class Actions(Parser):
    def __init__(self, btsio, players):
        super().__init__(btsio)
        self.players = players
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
        
    def del_player(self, id):
        try:
            del self.players[id]
        except KeyError:
            pass
        
    def player(self, id):
        try:
            sender = self.players[id].name
        except KeyError:
            sender = 'Unknown'
            print('UNKNOWN', id)
        except AttributeError:
            print('atttrerror', id) # fix: use namedtuple in newPlayer
        return sender
        
    def dump(self):
        sender = self.player(self.parse_uint())
        action = self.actions[self.parse_byte()]
        parsed = getattr(self, action)()
        return Action(sender=sender, action=action, parsed=parsed)

    def announceHandicap(self):
        return 'Handicapped '+self.parse_ushort()
        
    def broadcastPing(self):
        num = self.parse_byte()
        
        for _ in range(num):
            self.parse_byte()
            
        return 'Pings updated'
        
    def changeGameSettings(self):
        setting = self.parse_byte()
        val = self.parse_uint()
        
        return 'Settings changed'
        
    def changePlayerAdminRights(self):
        player = self.player(self.parse_uint())
        admin = self.parse_bool()
        
        if not admin:
            return 'Removed admin from '+player
        
        return 'Made '+player+' an admin'
        
    def changePlayerAvatar(self):
        return '/avatar '+ self.parse_str()
        
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
        
        return 'Moved '+ player +' to '+team
        
    def discMove(self):
        move = self.parse_byte()
        
        if move & 16 == 0:
            return 'wot'
         
        return move
        
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
                country=country
            )
        self.players[ID] = p
        
        return name+' joined'
        
    def removePlayer(self):
        ID = self.parse_ushort()
        player = self.player(ID)
        kicked = self.parse_bool()
        
        if kicked:
            reason = self.parse_str()
            
        ban = self.parse_bool()
        
        self.del_player(ID)
        
        if kicked:
            return '{} was {}: {}'.format(player, 'banned' if ban else 'kicked', reason)
        
        else:
            return '{} left'.format(player)
     
     
    def announceDesync(self):
        return 'Desynchronized'
