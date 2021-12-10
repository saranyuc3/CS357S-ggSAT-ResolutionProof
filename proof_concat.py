import glob
import os
import sys
import re
import random
from subprocess import call
import multiprocessing

tree = {}

res_proof = {}

leaf_res = {}


Gcnt = 0

respf = 0

def traverseTree(parent):    
    global tree
    global respf
    global leaf_res
    global Gcnt
    litL = tree[parent][0]
    litR = tree[parent][1]
    if litL != None:
        traverseTree(litL)
    if litR != None:
        traverseTree(litR)
    Gcnt+=1
    if litL==None and litR==None:
        nmL = '_'.join(tree[parent][2])+'_-'+parent.replace('$','')
        nmR = '_'.join(tree[parent][2])+'_'+parent.replace('$','')
        flag1 = 1
        flag2 = 1
        r1 = set(leaf_res[nmL][1])
        try:
            r1.remove(parent.replace('$',''))
        except:
            flag1 = 0
        r2 = set(leaf_res[nmR][1])
        try:
            r2.remove('-'+parent.replace('$',''))
        except:
            flag2 = 0
        if flag1==1 and flag2==1:    
            resolve = r1.union(r2)
            respf.write(str(Gcnt)+' '+parent.replace('$','')+' '+str(leaf_res[nmR][0])+' '+str(leaf_res[nmL][0])+' '+str(len(resolve))+' '+' '.join([i for i in resolve])+' '+str(len(resolve))+'\n')	
            tree[parent].append([Gcnt, resolve])
        elif flag1==0:
            tree[parent].append([leaf_res[nmL][0], leaf_res[nmL][1]])
            Gcnt-=1
        elif flag2==0:
            Gcnt-=1
            tree[parent].append([leaf_res[nmR][0], leaf_res[nmR][1]])
        
    else: 
        flag1 = 1
        flag2 = 1
        flag3 = 1
        flag4 = 1
        if tree[parent][0]!=None:        
            r1 = set(tree[tree[parent][0]][3][1])
        else:
            nmL = '_'.join(tree[parent][2])+'_-'+parent.replace('$','')
            r1 = set(leaf_res[nmL][1])
            flag3 = 0
        try:
            r1.remove(parent.replace('$',''))
        except:
            flag1 = 0
        if tree[parent][1]!=None:        
            r2 = set(tree[tree[parent][1]][3][1])
        else:
            nmR = '_'.join(tree[parent][2])+'_'+parent.replace('$','')
            r2 = set(leaf_res[nmR][1])
            flag4 = 0
        try:
            r2.remove('-'+parent.replace('$',''))
        except:
            flag2 = 0
        if flag1==1 and flag2==1:    
            resolve = r1.union(r2)
            respf.write(str(Gcnt)+' '+parent.replace('$','')+' '+str(tree[tree[parent][1]][3][0] if flag4==1 else leaf_res[nmR][0])+' '+str(tree[tree[parent][0]][3][0] if flag3==1 else leaf_res[nmL][0])+' '+str(len(resolve))+' '+' '.join([i for i in resolve])+' '+str(len(resolve))+'\n')	
            tree[parent].append([Gcnt, resolve])
        elif flag1==0:
            if flag3==1:
               tree[parent].append([tree[tree[parent][0]][3][0], tree[tree[parent][0]][3][1]])
            else:
               tree[parent].append([leaf_res[nmL][0], leaf_res[nmL][1]])
            Gcnt-=1
        elif flag2==0:
            Gcnt-=1
            if flag4==1:
               tree[parent].append([tree[tree[parent][1]][3][0], tree[tree[parent][1]][3][1]])
            else:
               tree[parent].append([leaf_res[nmR][0], leaf_res[nmR][1]])
    return 



def terminal(string):
	os.system(string)


  
if len(sys.argv) != 3:
	print("Usage: python3 run.py path_to_proof_files path_to_problem_file")
	sys.exit(0)
  
path = sys.argv[1]
path = path if path[-1] == "/" else path+"/"
files = glob.glob(path+"*.proof")

jobs = []

for fil in files:
#	terminal('python3 -m pkg2.main '+sys.argv[2]+' '+fil)
	p = multiprocessing.Process(target=terminal, args=('python3 -m pkg2.main '+sys.argv[2]+' '+fil,))
	jobs.append(p)
	p.start()

for proc in jobs:
	proc.join()

files = glob.glob(path+"*.res")

respf = open(re.sub('\.(\S+)','.proof',sys.argv[2]),'w')


for fil in files:
	res_proof = []
	leaf = fil.split('/')[-1].replace('n','-').rstrip('.res')
	with open(fil,'r') as f:
		data = f.read().split('\n')
		thres = int(re.match('\%RESA32  \d+  (\d+)',data[0]).group(1))
		res = data[-2].split(' ')
		if 'PROBLEMCLS:' == res[0]:
			leaf_res[leaf] = [int(res[1]),res[6:-1]] 
			continue
		if Gcnt==0:
			Gcnt = thres
			respf.write(data[0].replace('%RESA32  ','%RESA32   \n  ')+'\n                                                                               \n                                                                               \n                                                                               \n')
		for cls in data[2:-1]:
			nw_cls = cls.split(' ')
			if 'PROBLEMCLS:'==nw_cls[0]:
				continue
			nw_cls[0] = str(int(nw_cls[0])-thres+Gcnt)
			nw_cls[2] = str(int(nw_cls[2])-thres+Gcnt) if int(nw_cls[2])>thres else nw_cls[2]
			nw_cls[3] = str(int(nw_cls[3])-thres+Gcnt) if int(nw_cls[3])>thres else nw_cls[3]
			respf.write(' '.join(nw_cls)+'\n')
		leaf_res[leaf] = [int(res[0])-thres+Gcnt,res[5:-1]]
		Gcnt = Gcnt+int(res[0])-thres
	
for fil in files:
	trail = fil.split('/')[-1].replace('n','-').rstrip('.res').split('_')
	parent = trail[0]
	trl = []
	for lit in range(len(trail)-1,-1,-1):
		if '-' in trail[lit]:
			if trail[lit][1:] not in tree.keys():
				if trl!=[]: 
					tree[trail[lit][1:]]= [trl[len(trail)-lit-2],None,trail[:lit]]
					trl.append(trail[lit][1:])
				else:
					tree[trail[lit][1:]]= [None,None,trail[:lit]]
					trl.append(trail[lit][1:])
			else:
				nw_name = trail[lit][1:]
				while(1):
					if nw_name in tree.keys():
						if trail[:lit]==tree[nw_name][2]:
							if trl!=[]:
								tree[nw_name][0]= trl[len(trail)-lit-2]
								trl.append(nw_name)
							else:
								tree[nw_name][0]= None
								trl.append(nw_name)
							break
						else:
							nw_name = nw_name + '$'
					else:
						if trl!=[]:
							tree[nw_name]= [trl[len(trail)-lit-2],None,trail[:lit]]
							trl.append(nw_name)
						else:
							tree[nw_name]= [None,None,trail[:lit]]
							trl.append(nw_name)
						break

		else:			
			if trail[lit] not in tree.keys():
				if trl!=[]: 
					tree[trail[lit]]= [None,trl[len(trail)-lit-2],trail[:lit]]
					trl.append(trail[lit])
				else:
					tree[trail[lit]]= [None,None,trail[:lit]]
					trl.append(trail[lit])
			else:
				nw_name = trail[lit]
				while(1):
					if nw_name in tree.keys():
						if trail[:lit]==tree[nw_name][2]:
							if trl!=[]:
								tree[nw_name][1]= trl[len(trail)-lit-2]
								trl.append(nw_name)
							else:
								tree[nw_name][1]= None
								trl.append(nw_name)
							break
						else:
							nw_name = nw_name + '$'
					else:
						if trl!=[]:
							tree[nw_name]= [None,trl[len(trail)-lit-2],trail[:lit]]
							trl.append(nw_name)
						else:
							tree[nw_name]= [None,None,trail[:lit]]
							trl.append(nw_name)
						break


traverseTree(parent.replace('-',''))
