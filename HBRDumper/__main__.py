import sys
from pprint import pprint
from .dumper import dump
from .utils import *

def main(args=None):
    if len(sys.argv) < 2:
        file = "C:/Users/User/Desktop/sta/1GAME.hbr"
        # file = "C:/Users/User/Rand/HBMaps/ASDASD.hbr"
    else:
        file = ' '.join(sys.argv[1:])
    
    try:
        dumped = dump(file)
    except ParserError as e:
        print('ERROR:', e.reason)
    else:
        print(file, 'Successfuly dumped.')
        pprint(dumped)

if __name__ == '__main__':
    main()