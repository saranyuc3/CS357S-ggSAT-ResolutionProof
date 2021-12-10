import os
import sys
import random
from subprocess import call
import multiprocessing
import time
import json

tree = {}

def terminal(string):
    os.system(string)

def buildtree(literals, parent, depth):    
    global tree
    global paths
    dec_lit1 = random.choice(literals)
    dec_lit2 = random.choice(literals)
    if parent in tree.keys():
          tree[parent][0] = dec_lit1
          tree[parent][1] = dec_lit2    
    stopL = random.randint(0, 1)
    stopR = random.randint(0, 1)

    parent_clean = parent
    parent_clean = parent_clean.replace('$','')
    path = ['-'+lit if lit==parent_clean else lit for lit in tree[parent][2]]
    path.append(dec_lit1)
    nw_dec_lit1 = dec_lit1
    nw_dec_lit2 = dec_lit2
    while(1):
          if nw_dec_lit1 in tree.keys():
                nw_dec_lit1 = nw_dec_lit1+'$'
          else:
                break
   
    tree[nw_dec_lit1] = [None,None,path]
    while(1):
          if nw_dec_lit2 in tree.keys():
                nw_dec_lit2 = nw_dec_lit2+'$'
          else:
                break

    path = tree[parent][2].copy()
    path.append(dec_lit2)
    tree[nw_dec_lit2] = [None,None,path]
        
    if stopL==0 and len(tree[parent][2])<depth:
        temp_lit = literals.copy()
        temp_lit.remove(dec_lit1)
        buildtree(temp_lit,nw_dec_lit1,depth)

    if stopR==0 and len(tree[parent][2])<depth:
        temp_lit = literals.copy()
        temp_lit.remove(dec_lit2)
        buildtree(temp_lit,nw_dec_lit2,depth)    	  

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

tree[str(dec_lit)] = [None,None,[str(dec_lit)]]

temp_lit = [str(i) for i in literals]

temp_lit.remove(str(dec_lit))

buildtree(temp_lit, str(dec_lit), min(int(sys.argv[2])-1,len(literals)-1))


paths = []

try:
	with open(sys.argv[5],'r') as f:
		paths = json.load(f)
	
except IndexError:
	for key in tree.keys():
		if tree[key][0:2]==[None,None]:
			paths.append(tree[key][2].copy())
			temp = tree[key][2][:-1].copy()
			temp.append('-'+key.replace('$',''))
			paths.append(temp)
	

jobs = []
os.system('mkdir '+sys.argv[3])
os.system('mkdir outputs/tmp/')
t1 = time.time()
for path in paths:
	if sys.argv[4]=='s':
		terminal('python3 -m pkg.main '+sys.argv[1]+' '+sys.argv[3]+' '+"_".join([str(lit) for lit in path]).replace('-','n'))
	elif sys.argv[4]=='p':
		p = multiprocessing.Process(target=terminal, args=('python3 -m pkg.main '+sys.argv[1]+' '+sys.argv[3]+' '+"_".join([str(lit) for lit in path]).replace('-','n'),))
		jobs.append(p)
		p.start()
	else:
		sys.exit('Choose either p (parallel exec) or s (sequential exec)')	

if sys.argv[4]=='p':
	for proc in jobs:
		proc.join()

t2 = time.time()
t3 = time.time()
for path in paths:
	if sys.argv[4]=='s':
		terminal('python3 -m pkg3.main '+sys.argv[1]+' outputs/tmp/ '+"_".join([str(lit) for lit in path]).replace('-','n'))
	elif sys.argv[4]=='p':
		p = multiprocessing.Process(target=terminal, args=('python3 -m pkg.main '+sys.argv[1]+' outputs/tmp/ '+"_".join([str(lit) for lit in path]).replace('-','n'),))
		jobs.append(p)
		p.start()
	else:
		sys.exit('Choose either p (parallel exec) or s (sequential exec)')	
if sys.argv[4]=='p':
	for proc in jobs:
		proc.join()

t4 = time.time()
with open(sys.argv[3]+'/time.txt','w') as f:
	f.write("Instrumented time:{}\n".format(t2-t1))
	f.write("Uninstrumented time:{}\n".format(t4-t3))

