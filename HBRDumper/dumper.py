from collections import OrderedDict
import time
from .parser import Parser

class Dumper:
    def __init__(self, file):
        self.hbr = Parser(file)
        self.result = OrderedDict()
        
    def dump(self):
        self.dump_header()
        self.dump_discs()
        self.dump_players()

        return self.result

    def dump_header(self):
        header_order = [
            ('Version', self.hbr.parse_uint),
            ('i_HBRP', self.hbr.parse_uint),
            ('Replay length', self.hbr.parse_uint),
            ('i_deflate', self.hbr.deflate),
            ('i_First Frame', self.hbr.parse_uint),
            ('Room Name', self.hbr.parse_str),
            ('Locked', self.hbr.parse_bool),
            ('Score Limit', self.hbr.parse_byte),
            ('Time Limit', self.hbr.parse_byte),
            ('i_Rules Timer', self.hbr.parse_uint),
            ('i_Rules', self.hbr.parse_byte),
            ('i_Puck side', self.hbr.parse_side),
            ('i_Puck pos', self.hbr.parse_pos),
            ('Red score', self.hbr.parse_uint),
            ('Blue score', self.hbr.parse_uint),
            ('Current time', self.hbr.parse_double),
            ('Paused', self.hbr.parse_bool),
            ('Stadium', self.hbr.parse_stadium),
            ('In progress', self.hbr.parse_bool)
        ]

        for name, func in header_order:
            parsed = func()
            if 'i_' not in name:
                self.result[name] = parsed
                
        self.result['Replay length'] = time.strftime("%H:%M:%S", time.gmtime(self.result['Replay length'] / 60))
        self.result['Current time'] = time.strftime("%H:%M:%S", time.gmtime(self.result['Current time']))

    def dump_disc(self):
        disc_order = [
            ('X', self.hbr.parse_double),
            ('Y', self.hbr.parse_double),
            ('Speed x', self.hbr.parse_double),
            ('Speed Y', self.hbr.parse_double),
            ('Radius', self.hbr.parse_double),
            ('bCoef', self.hbr.parse_double),
            ('invMass', self.hbr.parse_double),
            ('Damping', self.hbr.parse_double),
            ('color', self.hbr.parse_uint),
            ('cMask', self.hbr.parse_uint),
            ('cGroup', self.hbr.parse_uint)
        ]
        for name, func in disc_order:
            parsed = func()
                
    def dump_discs(self):
        if self.result['In progress']:
            for _ in range(self.hbr.parse_uint()):
                self.dump_disc()

    def dump_player(self):
        player = OrderedDict()
        player_order = [
            ('ID', self.hbr.parse_uint),
            ('Name', self.hbr.parse_str),
            ('Admin', self.hbr.parse_bool),
            ('Team', self.hbr.parse_side),
            ('Number', self.hbr.parse_byte),
            ('Avatar', self.hbr.parse_str),
            ('Input', self.hbr.parse_uint),
            ('Autokick', self.hbr.parse_bool),
            ('Desynced', self.hbr.parse_bool),
            ('Country', self.hbr.parse_str),
            ('Handicap', self.hbr.parse_ushort),
            ('DiscID', self.hbr.parse_uint)
        ]
        for name, func in player_order:
            player[name] = func()
            
        return player['Name']
            
    def dump_players(self):
        players = self.hbr.parse_uint()
        player_list = []
        for player in range(players):
            player_list.append(self.dump_player())
        
        self.result['Players'] = player_list
   
def dump_hbr(file):
    hbr = Dumper(file)
    return hbr.dump()
