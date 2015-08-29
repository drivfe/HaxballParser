from .parser import Parser
from .utils import *

class ActionParser(Parser):
    def __init__(self, btsio, result, options):
        super().__init__(btsio)
        self.result = result
        self.rem_data_size = len(btsio)

        self.ph = PlayerHandler(self)

        self.pings_only_in_progress = options.get('pings_only_in_progress', False)
        self.action_ignore = set(options.get('actions_to_ignore', ['broadcastPing', 'discMove']))

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

    @property
    def in_progress(self):
        return self._in_progress

    @in_progress.setter
    def in_progress(self, val): # Start/Stop counting playing-time when game is started/stopped.
        self._in_progress = val
        if val:
            self.ph.start_pt()
        else:
            self.ph.stop_pt()

    def player(self, pid):
        return self.ph.get_from_id(pid)

    def dump(self):
        self.cframe = 0
        self.replaytime = 0
        self.cur_senderID = 0
        self.in_progress = self.result['In progress'] and not self.result['Paused']

        action_list = []

        # Stuff to make parsing faster
        dnext = self.dump_next
        pos = self.fh.tell
        alappend = action_list.append
        pb = self.parse_bool
        pu = self.parse_uint

        while pos() < self.rem_data_size:
            if pb(): # True if this is a different frame.
                self.cframe += pu()
                self.replaytime = self.cframe / 60
            
            action = dnext()
        
            if action.parsed and action.action not in self.action_ignore:
                alappend(action)
        
        self.finished()

        return action_list
            
    def finished(self):
        # Make sure Player's frames_in are updated
        self.in_progress = False

        # Merge players and player_bin
        [self.ph.players.append(np) for np in self.ph.player_bin]
 
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
        if not self.pings_only_in_progress or (self.in_progress and self.pings_only_in_progress):
            self.ph.update_pings(pings)
            
        return 'Pings updated'
        
    def changeGameSettings(self):
        self.parse_byte() # setting
        self.parse_uint() # val
        
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
        
        self.ph.move_player(player, team)
        
        return 'Moved '+ player.name +' to '+ team
        
    def discMove(self):
        return self.fh.read(1) # No need to unpack, for now.
        
    def stopMatch(self):
        self.in_progress = False
        return 'Stopped match'
        
    def startMatch(self):
        self.in_progress = True
        return 'Started match'
    
    def logicUpdate(self):
        return 'Logic update'
    
    def playerChat(self):
        return Message(self.cur_senderID, self.in_progress, self.parse_str())
        
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

        self.ph.add_player(p)
        
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
            
        self.ph.remove_player(ID)
            
        if kicked:
            return '{} was {}: {}'.format(player.name, 'banned' if ban else 'kicked', reason)
        
        else:
            return '{} left'.format(player.name)
     
    def announceDesync(self):
        return 'Desynchronized'