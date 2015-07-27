import sys
from pprint import pprint
from .dumper import dump_hbr
from .utils import *

def main(args=None):
    if len(sys.argv) < 2:
        file = "C:/Users/User/Desktop/1GAME.hbr"
    else:
        file = ' '.join(sys.argv[1:])
    
    dumped = dump_hbr(file)
    pprint(dumped)

if __name__ == '__main__':
    main()