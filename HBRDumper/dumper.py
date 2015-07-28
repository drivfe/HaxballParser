import sys
from collections import OrderedDict
from .parser import Parser
from .actionparser import ActionParser
from .utils import *

class Dumper:
    def __init__(self, file):
        self.hbr = Parser(file)
        self.result = OrderedDict()
        
    def dump(self):
        version = self.hbr.parse_uint()
        if version < 12:
            raise ParserError(
                'Replay version {} is not supported.'.format(version)
            )
        
        self.result['Version'] = version
        
        self.dump_header()
        self.dump_discs()
        self.dump_players()
        self.dump_actions()
        
        return self.result

    def dump_header(self):
        
            
        header_order = [
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
            ('Current replay time', self.hbr.parse_double),
            ('Paused', self.hbr.parse_bool),
            ('Stadium', self.hbr.parse_stadium),
            ('In progress', self.hbr.parse_bool)
        ]

        for name, func in header_order:
            parsed = func()
            if 'i_' not in name:
                self.result[name] = parsed
        
        self.result['Replay length'] = format_time(self.result['Replay length'] / 60)
        
        if self.result['Current replay time'] < 0:
            self.result['Current replay time'] = 0
        self.result['Current replay time'] = format_time(self.result['Current replay time'])

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
            
        p = Player(
                ID=player['ID'],
                name=player['Name'],
                admin=player['Admin'],
                country=player['Country'],
                team=player['Team'],
                avatar=player['Avatar']
            )
        return p
            
    def dump_players(self):
        amt = self.hbr.parse_uint()
        pls = []
        for player in range(amt):
            pls.append(self.dump_player())
        
        self.result['Players'] = pls
    
    def dump_actions(self):
        rem_data = self.hbr.fh.read()
        self.hbr = ActionParser(rem_data, self.result['Players'])
      
        self.result['Actions'] = self.hbr.dump()
        
def dump(file):
    with open(file, 'rb') as fh:
        data = fh.read()
        
    hbr = Dumper(data)
    return hbr.dump()
