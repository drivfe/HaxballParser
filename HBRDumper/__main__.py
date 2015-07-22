import sys
from .dumper import dump_hbr

def main(args=None):
    if len(sys.argv) < 2:
        file = "C:/Users/User/Desktop/1GAME.hbr"
    else:
        file = ''.join(sys.argv[1:])

    dumped = dump_hbr(file)
    for k, v in dumped.items():
        print(k+':', v)

if __name__ == '__main__':
    main()