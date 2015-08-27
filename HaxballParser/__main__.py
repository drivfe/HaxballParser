import sys
import os
import glob
from timeit import default_timer as t

from HaxballParser.dumper import dump
from HaxballParser.utils import *

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
            
    print('Dumped file(s) will be saved in the directory "{}"'.format(dirn))
    suc, fail, tottime = 0, 0, t()
    for file in files:
        basen, ext = os.path.basename(file).split('.')
        hbrdump = os.path.join(dirn, basen+'.txt')
        try:
            start = t()
            dumped = dump(file)
        except ParserError as e:
            print('"{}" -> ERROR: {}'.format(basen, e.reason))
            fail+=1
        else:
            print('"{}" -> SUCCESS: dumped to hbrdumps/{}.txt ({}ms)'.format(basen, basen, int((t()-start)*1000)))
            with open(hbrdump, 'w+') as f:
                f.write(dumped.prettify())
            suc+=1
    tottime = int((t()-tottime)*1000)

    print("\nSUCCESSFUL DUMPS: {}\nFAILED DUMPS: {}\n{}ms ({}ms/hbr)".format(suc, fail, tottime, int(tottime/suc) if suc > 0 else 0))

if __name__ == '__main__':
    main()