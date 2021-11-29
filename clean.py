import sys

with open(sys.argv[1], 'r') as f:
    lines = [
        line.strip().split() for line in f.readlines()
        if (not (line.startswith('c') or
                 line.startswith('%') or
                 line.startswith('0'))
            and line != '\n')
    ]


if lines[0][:2] == ['p', 'cnf']:
    count_literals, count_clauses = map(int, lines[0][-2:])
else:
    raise FileFormatError('Number of literals and clauses are not declared properly.')

with open(sys.argv[1], 'w') as f:
    f.write('p cnf ' + str(count_literals) + ' '+ str(len(lines)-1)+'\n')
    for i in lines[1:]:
    	f.write(' '.join(i)+'\n')

