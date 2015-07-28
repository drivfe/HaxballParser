import sys
import os
import glob
from timeit import default_timer as t
from pprint import pformat
from .dumper import dump
from .utils import *

def main(args=None):
    args = ' '.join(sys.argv[1:])
    files = []
    
    if len(sys.argv) < 2:
        args = os.getcwd()
        
    if os.path.isdir(args) and os.path.exists(args):
        files = glob.glob(os.path.join(args, '*.hbr'))
        if len(files) < 1:
            sys.exit('No .hbr files found in {}.'.format(args))
        
    if os.path.isfile(args) and os.path.exists(args):
        files = [args]
        
    if len(files) < 1:
        sys.exit('File {} does not exist.'.format(args))
        
    dirn = os.path.dirname(files[0])
    dirn = os.path.join(dirn, 'hbrdumps')
    if not os.path.exists(dirn):
        os.makedirs(dirn)
            
    print('.hbrdump file(s) will be saved in the directory "{}"'.format(dirn))
    for file in files:
        basen = os.path.basename(file)
        hbrdump = os.path.join(dirn, basen+'dump')
        try:
            start = t()
            dumped = dump(file)
        except ParserError as e:
            print('"{}" -> ERROR: {}'.format(basen, e.reason))
        else:
            print('"{}" -> SUCCESS: dumped to {} ({}ms)'.format(basen, hbrdump, int((t()-start)*1000)))
            with open(hbrdump, 'w+') as f:
                f.write(pformat(dumped))

if __name__ == '__main__':
    main()