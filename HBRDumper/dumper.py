import io
from pprint import pformat
from collections import OrderedDict
from .parser import Parser
from .actionparser import ActionParser
from .utils import *

class DumpResponse:
    def __init__(self, result):
        self.result = result

    def __repl__(self):
        return self.result

    def prettify(self, includeraw=True):
        r = self.result
        sb = io.StringIO()
        line = lambda s='', b=sb: b.write(s+'\n')

        # Replay info
        line('REPLAY INFO')
        line('  Version {}'.format(r['Version']))
        line('  Length: {}'.format(r['Replay length']))
        line()

        # Room info
        line('ROOM INFO')
        line('  Room name: {}'.format(r['Room Name']))
        line('  Scores: Red {} - {} Blue'.format(r['Red score'], r['Blue score']))
        line('  Time limit: {} - Score limit: {}'.format(r['Time Limit'], r['Score Limit']))
        line('  Current match time: {}'.format(r['Current match time']))
        line('  Match in progress: {}'.format(r['In progress']))
        line()

        # Players
        line('PLAYERS LIST')
        redp = find_by_attr_val(r['Players'], {'team': 'Red', 'orig': True}, True)
        bluep = find_by_attr_val(r['Players'], {'team': 'Blue', 'orig': True}, True)
        specp = find_by_attr_val(r['Players'], {'team': 'Spectator', 'orig': True}, True)
        
        if len(redp) > 0:
            line('  Red:')
            [line('    '+p.name) for p in redp]

        if len(bluep) > 0:
            line('  Blue:')
            [line('    '+p.name) for p in bluep]
        
        if len(specp) > 0:
            line('  Spectators:')
            [line('    '+p.name) for p in specp]

        line('  Throughout the replay:')
        joined = find_by_attr_val(r['Players'], {'orig': False}, True)
        left = find_by_attr_val(r['Players'], {'removed': True}, True)
        if len(joined) > 0:
            line('    Joined:')
            [line('      '+p.name) for p in joined]
        if len(left) > 0:
            line('    Left/Kicked/Banned:')
            [line('      '+p.name) for p in left]
        line()

        # Actions

        pdict = {p.ID: p for p in r['Players']}

        line('ACTION LIST')
        acts = r['Actions']
        for a in acts:
            if pdict.get(a.senderID, 0):
                frmt = '({}) {} -> {}'.format(
                        format_time(a.time),
                        pdict[a.senderID].name,
                        a.parsed
                    )
                line(frmt)
        line()

        # Raw dictionary
        if includeraw:
            line('RAW DICTIONARY')
            sb.write(pformat(r))

        pretty = sb.getvalue()
        sb.close()

        return pretty

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
        
        if self.hbr.nxt(4) != b'HBRP':
            raise ParserError('Not a valid .hbr file.')
        
        self.dump_header()
        self.dump_discs()
        self.dump_players()
        self.dump_colors()
        self.dump_actions()
        
        return DumpResponse(self.result)

    def dump_header(self):
        header_order = [
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
            ('Current match time', self.hbr.parse_double),
            ('Paused', self.hbr.parse_bool),
            ('Stadium', self.hbr.parse_stadium),
            ('In progress', self.hbr.parse_bool)
        ]

        for name, func in header_order:
            parsed = func()
            if 'i_' not in name:
                self.result[name] = parsed
        
        self.result['Replay length'] = format_time(self.result['Replay length'] / 60)

        if str(self.result['Current match time']).lower() == 'nan':
            self.result['Current match time'] = 0
        self.result['Current match time'] = format_time(self.result['Current match time'])

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
        player = {}
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
    
    def dump_colors(self):
        for _ in range(2): # Two teams
            self.hbr.parse_ushort() # Angle
            self.hbr.parse_uint() # Textcolor
            clrs = self.hbr.parse_byte() # Amount of colors
            for _ in range(clrs):
                self.hbr.parse_uint()

    def dump_actions(self):
        rem_data = self.hbr.fh.read()
        self.hbr = ActionParser(rem_data, self.result['Players'])
      
        self.result['Actions'] = self.hbr.dump()
        
def dump(file):
    with open(file, 'rb') as fh:
        data = fh.read()
        
    resp = Dumper(data)
    return resp.dump()
