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
        'decisions',
        type=str,
        nargs='?',
        help='decisions taken by Look-Ahead solver in one branch')
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

    if args.filename is None or args.decisions is None:
        parser.print_help()
        exit()
    args.decisions = args.decisions.replace('n','-')
    print('problem file: ',args.filename.split('/')[-1])
    print('decision path: ',args.decisions)
    solver.logger.setLevel(args.loglevel)
    solver = getattr(solvers, args.heuristics)(args.filename, args.decisions)
    _, _, answer = solver.run(args.decisions)
    print(answer)
