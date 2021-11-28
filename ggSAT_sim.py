import os
import sys
import random
from subprocess import call
import multiprocessing

tree = {}

def terminal(string):
    os.system(string)

def buildtree(literals, parent, depth):    
    global tree
    global paths
    dec_lit1 = random.choice(literals)
    dec_lit2 = random.choice(literals)
    tree[parent][0] = dec_lit1
    tree[parent][1] = dec_lit2    
    stopL = random.randint(0, 1)
    stopR = random.randint(0, 1)

    path = [-lit if lit==parent else lit for lit in tree[parent][2]]
    path.append(dec_lit1)
    tree[dec_lit1] = [None,None,path]
    path = tree[parent][2].copy()
    path.append(dec_lit2)
    tree[dec_lit2] = [None,None,path]


    if stopL==0 and len(tree[parent][2])<depth:
        temp_lit = literals.copy()
        temp_lit.remove(dec_lit1)
        buildtree(temp_lit,dec_lit1,depth)

    if stopR==0 and len(tree[parent][2])<depth:
        temp_lit = literals.copy()
        temp_lit.remove(dec_lit2)
        buildtree(temp_lit,dec_lit2,depth)    	  

    return 
    	

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

for line in lines[1:]:
    if line[-1] != '0':
        raise FileFormatError('Each line of clauses must end with 0.')
    clause = list(map(int, line[:-1]))
    literals.update(map(abs, clause))

depth = min(int(sys.argv[2]),random.randint(1,len(literals)))

dec_lit = random.choice(list(literals))

tree[dec_lit] = [None,None,[dec_lit]]

temp_lit = [i for i in literals]

temp_lit.remove(dec_lit)

buildtree(temp_lit, dec_lit, min(int(sys.argv[2])-1,len(literals)-1))

paths = []

for key in tree.keys():
    if tree[key][0:2]==[None,None]:
    	paths.append(tree[key][2].copy())
    	temp = tree[key][2][:-1].copy()
    	temp.append(-key)
    	paths.append(temp)

jobs = []
for path in paths:
	if sys.argv[3]=='s':
		terminal('python3 -m pkg.main '+sys.argv[1]+' '+"_".join([str(lit) for lit in path]).replace('-','n'))
	elif sys.argv[3]=='p':
		p = multiprocessing.Process(target=terminal, args=('python3 -m pkg.main '+sys.argv[1]+' '+"_".join([str(lit) for lit in path]).replace('-','n'),))
		jobs.append(p)
		p.start()
	else:
		sys.exit('Choose either p (parallel exec) or s (sequential exec)')	

if sys.argv[3]=='p':
	for proc in jobs:
		proc.join()


