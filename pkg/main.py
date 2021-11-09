"""
SAT solver using CDCL
"""

import argparse
import os
from pkg.pysat import solver
from pkg.pysat import branch_heuristics as solvers


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reads a file and try to determine satisfiability by CDCL.'
        ' Example usage: python3 -m pkg.main test/sample.cnf'
    )
    parser.add_argument(
        'filename',
        type=str,
        nargs='?',
        help='path of .cnf file')
    parser.add_argument(
        'heuristics',
        type=str,
        nargs='?',
        default='FrequentVarsFirstSolver',
        help='choose heuristics to branch variable'
             ': OrderedChoiceSolver '
             '| RandomChoiceSolver '
             '| FrequentVarsFirstSolver (default) '
             '| DynamicLargestIndividualSumSolver')
    parser.add_argument(
        '--loglevel',
        default='WARNING',
        nargs='?',
        help='level of logging (WARNING, DEBUG, etc.)')

    args = parser.parse_args()

    if args.filename is None:
        parser.print_help()
        exit()

    filename = args.filename.split('/')
    path = '/'.join(filename[:-1])
    filename = filename[-1]
    
    filelist = []
    
    for file in os.listdir(path):
             if file.startswith(filename.removesuffix('.cnf')) and file.endswith('.sol'):
                filelist.append(file)
                
    for files in filelist:            
      print(files)
      suffix = files.removeprefix(filename.removesuffix('.cnf')+',').removesuffix('.sol')
      solver = getattr(solvers, args.heuristics)(path+'/'+filename, path+'/'+files, suffix)
      solver.run()

