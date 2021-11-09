"""
SAT solver using CDCL
"""
import os
import sys
import random

with open(sys.argv[1]) as f:
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

literals = set()
clauses = []

for line in lines[1:]:
    if line[-1] != '0':
        raise FileFormatError('Each line of clauses must end with 0.')
    clause = list(map(int, line[:-1]))
    literals.update(map(abs, clause))
    clauses.append(clause)

size = random.randint(1,len(literals))

dec_lit = random.sample(literals, size%10)


for lit in range(size%10):
     if random.randint(0, 1):
          dec_lit[lit] = -dec_lit[lit]


               

count_clauses += len(dec_lit)

suffix = ''

for lit in dec_lit:
    suffix = suffix+','+str(lit)



file_name = sys.argv[1].split('/')[-1]

with open(sys.argv[2]+'/'+file_name.rstrip('.cnf')+suffix+'.cnf','w') as f:
    f.write('p cnf ' + str(count_literals) + ' '+ str(count_clauses)+'\n') 
    for i in clauses:
       for j in i:
           f.write(str(j)+' ')
       f.write('0\n')
    for i in dec_lit:
       f.write(str(i)+' 0\n')
       
os.system('./cadical '+sys.argv[2]+'/'+file_name.rstrip('.cnf')+suffix+'.cnf' +' --no-binary ' + sys.argv[2]+'/'+file_name.rstrip('.cnf')+suffix+'.sol')            

