from .parser import Parser
from .utils import *

class ActionParser(Parser):
    def __init__(self, btsio, result, options):
        super().__init__(btsio)
        self.result = result
        self.players = result['Players']
        self.in_progress = result['In progress'] and not result['Paused']
        self.only_in_progress = options.get('only_in_progress', False)
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
            'announceHandicap',
            'changeTeamColors'
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
        return find_by_attr_val(self.players, {'ID': id})

    def dump(self):
        cframe = 0
        action_list = []
        action_ignore = ['discMove', 'broadcastPing']
        
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

            if action.parsed and action.action not in action_ignore and action.senderID < 1000:
                alappend(action)
        
        self.finished()

        return action_list
            
    def finished(self):
        # Merge players and player_bin
        [self.players.append(np) for np in self.player_bin]
 
    def dump_next(self):
        self.cur_senderID = self.parse_uint()
        action = self.actions[self.parse_byte()]
        parsed = getattr(self, action)()
        
        return Action(time=self.replaytime, senderID=self.cur_senderID, action=action, parsed=parsed)
        
    def changeTeamColors(self):
        side = self.parse_side()
        coloramt = self.parse_byte()
        for _ in range(min(coloramt, 3)):
            self.parse_uint()
        self.parse_ushort() # Angle
        self.parse_uint() # Textcolor

        return 'Colors changed for the {} team.'.format(side)

    def announceHandicap(self):
        return 'Handicap set to '+ str(self.parse_ushort())
        
    def broadcastPing(self):
        num = self.parse_byte()
        
        # Ugly but faster
        pings = [self.parse_byte()*4 for p in range(num)]
        if not self.only_in_progress or (self.in_progress and self.only_in_progress):
            [self.players[p].pings.append(pings[p]) for p in range(num)]
            
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
        paused = self.parse_bool() # True = paused
        self.in_progress = not paused

        return 'Game paused' if paused else 'Game unpaused'
        
    def changeStadium(self):
        l = self.parse_uint()
        stp = Parser(self.nxt(l))
        stp.parse_byte() # Don't know

        sname = stp.parse_stadium()

        if l != 3:
            sname = 'Custom'

        del stp
        return 'Map changed to ' + sname
        
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
        self.in_progress = False
        return 'Stopped match'
        
    def startMatch(self):
        self.in_progress = True
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