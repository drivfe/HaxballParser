from .parser import Parser
from .utils import *

class ActionParser(Parser):
    def __init__(self, btsio, players):
        super().__init__(btsio)
        self.players = players
        self.rem_data_size = len(btsio)
        self.replaytime = 0
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
            p = find_by_attr_val(self.players, 'ID', id)
            if p:
                del self.players[self.players.index(p)]
        except KeyError:
            pass
        
    def player(self, id, attr='name', obj=False):
        sender = find_by_attr_val(self.players, 'ID', id)
        if sender and not obj:
            sender = getattr(sender, attr)
        
        return sender
        
    def dump(self):
        cframe = 0
        action_list = []
        action_ignore = ['discMove', 'broadcastPing']
        
        self.nxt(14) # I don't know what the first 14 bytes are.

        while self.pos() < self.rem_data_size:
            if self.parse_bool(): # True if this is a different frame.
                cframe += self.parse_uint()
                self.replaytime = cframe / 60
            
            action = self.dump_next()
            if action.parsed != None and action.action not in action_ignore:
                action_list.append(action)
                
        return action_list
        
    def dump_next(self):
        current_time = format_time(self.replaytime)
        senderID = self.parse_uint()
        action = self.actions[self.parse_byte()]
        parsed = getattr(self, action)()
        
        return Action(time=current_time, senderID=senderID, action=action, parsed=parsed)
        
    def announceHandicap(self):
        return 'Handicap set to '+ str(self.parse_ushort())
        
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
        player = self.player(self.parse_uint(), obj=True)
        admin = self.parse_bool()
        player.admin = admin
        
        if not admin:
            return 'Removed admin from '+ player.name
        
        return 'Made '+ player.name +' an admin'
        
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
        player = self.player(self.parse_uint(), obj=True)
        team = self.parse_side()
        
        if player == None:
            return None
            
        if team == player.team: # player was not moved, glitch.
            return None
        
        player.team = team
        
        return 'Moved '+ player.name +' to '+ team
        
    def discMove(self):
        move = self.parse_byte()
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
                country=country,
                team='Spectator',
                avatar=''
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
            return '{} was {}: {}'.format(player, 'banned' if ban else 'kicked', reason)
        
        else:
            return '{} left'.format(player)
     
     
    def announceDesync(self):
        return 'Desynchronized'
