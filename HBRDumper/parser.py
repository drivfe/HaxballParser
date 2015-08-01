import socket
import struct
import zlib
import io
import string
from .utils import ParserError

class Parser:
    def __init__(self, btsio):
        self.fh = io.BytesIO(btsio)
    
    def pos(self):
        return self.fh.tell()
    
    def nxt(self, amount):
        return self.fh.read(amount)

    def parse_uint(self):
        bts = self.nxt(4)
        unpacked = struct.unpack("<I", bts)[0]
        return socket.ntohl(unpacked)

    def parse_ushort(self):
        bts = self.nxt(2)
        unpacked = struct.unpack("<H", bts)[0]
        return socket.ntohs(unpacked)
        
    def parse_str(self):
        strlen = self.parse_ushort()
        result = b""
        
        for c in range(strlen):
            try:
                result += bytes([self.parse_byte()])
            except:
                pass

        fs = result.decode('ascii', errors='ignore')
        return ''.join(filter(lambda x: x in string.printable, fs))

    def parse_byte(self):
        bts = self.nxt(1)
        return struct.unpack("<B", bts)[0]

    def parse_bool(self):
        # n = ord(self.nxt(1))
        # if n > 2 or n < 0:
        #     print('BOOL ERROR', n)
        return ord(self.nxt(1)) == 1 # 0 = false, 1 = true

    def parse_side(self):
        side = self.parse_byte()
        if side == 1:
            return 'Red'
        elif side == 2:
            return 'Blue'
        elif side == 0:
            return 'Spectator'
        else:
            return 'parse_side() error'

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
            raise ParserError('Custom stadiums are not supported.')
        if b >= len(maps): # Bug?
            return 'BUG'
        return maps[b]

    def deflate(self):
        decompressed = zlib.decompress(self.fh.read())
        self.fh.close()

        self.fh = io.BytesIO()
        self.fh.write(decompressed)
        self.fh.seek(0)