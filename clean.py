import sys
import glob

def clean(fil):
  with open(fil, 'r') as f:
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

  with open(fil, 'w') as f:
    f.write('p cnf ' + str(count_literals) + ' '+ str(len(lines)-1)+'\n')
    for i in lines[1:]:
    	f.write(' '.join(i)+'\n')

files = glob.glob("./uuf50-218/*.cnf")
for fil in files:
  print(fil)
  clean(fil)
