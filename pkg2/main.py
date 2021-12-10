"""
SAT solver using CDCL
"""

import argparse
import os
from pkg2.pysat import solver
from pkg2.pysat import branch_heuristics as solvers


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reads a file and try to determine satisfiability by CDCL.'
        ' Example usage: python3 -m pkg2.main test/sample.cnf'
    )
    
    parser.add_argument(
        'filename',
        type=str,
        nargs='?',
        help='path of .cnf file')
    
    #parser.add_argument(
    #    'trail',
    #    type=str,
    #    nargs='?',
    #    help='path of file containing branching decisions')
    
    parser.add_argument(
        'conflicts',
        type=str,
        nargs='?',
        help='path of file containing sub problem conflicts')
    
    parser.add_argument(
        'heuristics',
        type=str,
        nargs='?',
        default='ForcedBranch',
        help='choose heuristics to branch variable'
             ': OrderedChoiceSolver '
             '| RandomChoiceSolver '
             '| FrequentVarsFirstSolver (default) '
             '| DynamicLargestIndividualSumSolver'
             '| ForcedBranch')
    
    parser.add_argument(
        '--loglevel',
        default='WARNING',
        nargs='?',
        help='level of logging (WARNING, DEBUG, etc.)')
    
    
    args = parser.parse_args()

    if args.filename is None:
        parser.print_help()
        exit()
    print('\n\n\n'+args.conflicts)
    solver.logger.setLevel(args.loglevel)
    solver = getattr(solvers, args.heuristics)(args.filename, args.conflicts)
    _, _, answer = solver.run()
    print(answer)
