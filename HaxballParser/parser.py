import socket
import struct
import zlib
import io
from .utils import ParserError

class Parser:
    def __init__(self, btsio):
        self.fh = io.BytesIO(btsio)
        self.nxt = self.fh.read

    def parse_uint(self):
        bts = self.nxt(4)
        unpacked = struct.unpack("<I", bts)[0]
        return socket.ntohl(unpacked)

    def parse_ushort(self):
        bts = self.nxt(2)
        unpacked = struct.unpack("<H", bts)[0]
        return socket.ntohs(unpacked)
        
    def parse_str(self):
        length = self.parse_ushort()
        result = struct.unpack('<{}s'.format(length), self.nxt(length))[0]

        return result.decode('ascii', errors='ignore')

    def parse_byte(self):
        return ord(self.nxt(1))

    def parse_bool(self):
        return self.nxt(1) == b'\x01' # ord(self.nxt(1)) == 1

    def parse_side(self):
        side = self.parse_byte()
        if side == 1:
            return 'Red'
        elif side == 2:
            return 'Blue'
        elif side == 0:
            return 'Spectator'
        else:
            raise ParserError('parse_side() error.')


    def parse_double(self):
        bts = self.nxt(8)[::-1]
        unpacked = struct.unpack("<d", bts)[0]
        return unpacked
            
    def parse_pos(self):
        return {'x': self.parse_double(), 'y': self.parse_double()}

    def parse_stadium(self):
        maps = [
            'Classic',
            'Easy',
            'Small',
            'Big',
            'Rounded',
            'Hockey',
            'Big Hockey',
            'Big Easy',
            'Big Rounded',
            'Huge'
        ]
        
        b = self.parse_byte()

        if b == 255:
            return "[CUSTOM] {}".format(self.parse_custom_stadium())

        return maps[b]

    def parse_custom_stadium(self):
        stadium_name = self.parse_str()

        # Background
        self.parse_byte() # bg type
        self.parse_double() # bg width
        self.parse_double() # bg height
        self.parse_double() # bg kickoff radius
        self.parse_double() # bg corner radius
        self.parse_double() # bg goal line
        self.parse_uint() # bg color

        # Camera
        self.parse_double() # camera width
        self.parse_double() # camera height

        # Spawn
        self.parse_double() # spawn distance

        # Vertices
        for _ in range(self.parse_byte()):
            self.parse_pos() # position
            self.parse_double() # bCoef
            self.parse_uint() # cMask
            self.parse_uint() # cGroup

        # Segments
        for _ in range(self.parse_byte()):
            self.parse_byte() # v0
            self.parse_byte() # v1
            self.parse_double() # bCoef
            self.parse_uint() # cMask
            self.parse_uint() # cGroup
            self.parse_double() # curve
            self.parse_bool() # visible
            self.parse_uint() # color

        # Planes
        for _ in range(self.parse_byte()):
            self.parse_pos() # position
            self.parse_double() # distance
            self.parse_double() # bCoef
            self.parse_uint() # cMask
            self.parse_uint() # cGroup

        # Goals
        for _ in range(self.parse_byte()):
            self.parse_pos() # position 0
            self.parse_pos() # position 1
            self.parse_side() # team

        # Discs
        for _ in range(self.parse_byte()):
            self.parse_pos() # position
            self.parse_double() # speedx
            self.parse_double() # speedy
            self.parse_double() # radius
            self.parse_double() # bCoef
            self.parse_double() # invMass
            self.parse_double() # damping
            self.parse_uint() # color
            self.parse_uint() # cMask
            self.parse_uint() # cGroup

        # Player physics
        self.parse_double() # bCoef
        self.parse_double() # invMass
        self.parse_double() # damping
        self.parse_double() # acceleration
        self.parse_double() # kickingAcceleration
        self.parse_double() # kickingDamping
        self.parse_double() # kickingStrength

        # Ball physics
        self.parse_pos() # Not important
        self.parse_pos() # Not important
        self.parse_double() # radius
        self.parse_double() # bCoef
        self.parse_double() # invMass
        self.parse_double() # damping
        self.parse_uint() # color 
        self.parse_uint() # cMask
        self.parse_uint() # cGroup

        return stadium_name

    def deflate(self, inflate=False):
        data = self.nxt()
        if inflate:
            decompressed = zlib.decompress(data, -15)

        else:
            decompressed = zlib.decompress(data)

        self.fh.truncate(0)
        self.fh.seek(0)
        self.fh.write(decompressed)
        self.fh.seek(0)