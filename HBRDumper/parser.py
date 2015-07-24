import socket, struct, zlib
from tempfile import TemporaryFile

class Parser:
    def __init__(self, filename):
        self.fh = open(filename, "rb")
    
    def nxt(self, amount):
        cb = self.fh.read(amount)
        return cb

    def parse_uint(self):
        bts = self.nxt(4)
        unpacked = struct.unpack("<I", bts)[0]
        result = socket.ntohl(unpacked)
        return result

    def parse_ushort(self):
        bts = self.nxt(2)
        unpacked = struct.unpack("<H", bts)[0]
        return socket.ntohs(unpacked)
        
    def parse_str(self):
        strlen = self.parse_ushort()
        result = b""
        
        for c in range(strlen):
            result += bytes([self.parse_byte()])

        return result.decode('ascii', errors='ignore')

    def parse_byte(self):
        bts = self.nxt(1)
        unpacked = struct.unpack("<B", bts)[0]
        return unpacked

    def parse_bool(self):
        n = ord(self.nxt(1))
        if n > 2 or n < 0:
            print('BOOL ERROR', n)
        return n == 1 # 0 = false, 1 = true

    def parse_side(self):
        side = self.parse_byte()
        if side == 0:
            return 'Red'
        elif side == 1:
            return 'Blue'
        elif side == 2:
            return 'Spectator'
        else:
            return 'parse_side() error'

    def parse_double(self):
        bts = self.nxt(8)
        unpacked = struct.unpack("<d", bts)[0]
        # rev = int(str(unpacked)[::-1])
        # result = rev/10000000
        return unpacked
            
    def parse_pos(self):
        pos = {'x': self.parse_double(), 'y': self.parse_double()}
        return pos

    def parse_stadium(self):
        b = self.parse_byte()
        if b != 255:
            return "Normal", b
        else:
            return "Custom", b

    def deflate(self):
        decompressed = zlib.decompress(self.fh.read())
        self.fh.close()

        self.fh = TemporaryFile()
        self.fh.write(decompressed)
        self.fh.seek(0)
        
        return 'Rest of file has been deflated'