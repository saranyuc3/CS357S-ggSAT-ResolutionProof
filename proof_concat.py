import glob 
import sys
import os
import shutil

def combine_proofs(clause_set_1, clause_set_2, branch_variable):
  '''
  Clause_set_1 = conflict clauses (list of strings) of branch_variable branch
  clause_set_2 = conflict_clauses (list of strings) of ~branch_variable branch
  returns: set of combined clauses
  '''

  branch_variable_n = branch_variable[1:] if branch_variable[0] == "-" else "-" + branch_variable
  
  for i in range(len(clause_set_1)):
    clause_set_1[i] = clause_set_1[i][:-2]+branch_variable_n+" 0\n"
  

  for i in range(len(clause_set_2)):
    clause_set_2[i] = clause_set_2[i][:-2]+branch_variable+" 0\n"
  #print(clause_set_1)
  return clause_set_1 + clause_set_2 + ["0\n"]


def sorting_key(tup):
  return -tup[0]


def order_proofs(list_of_proof_files):
  '''
  decides order in which proofs must be combined
  returns: ordered list of tuples denoting proof files to be joined together
  '''
  temp = []
  ord_list = []
  
  for fil in list_of_proof_files:
    fil = fil[:-6]
    
    path = "/".join(fil.split("/")[:-1])

    fil = fil.split("/")[-1]
    lenfil = len(fil.split("_"))
    temp.append((len(fil), fil))

  temp.sort(key=sorting_key)
  
  for fil_l, fil in temp:
    fil_temp = fil.split("_")
    #print(fil_temp)
    if "_" in fil:
      fil_n = fil_temp[0] #first literal
      for l in fil_temp[1:-1]:
        fil_n = fil_n + "_" + l # second literal to second last literal
      fil_n = fil_n + "_"
    else:
      fil_n = ""

    #negation of last literal
    neg_lit = fil_temp[-1][1:] if fil_temp[-1][0] == "n" else "n" + fil_temp[-1]
    
    if fil_n != "":
      temp.append((len(fil_n),fil_n[:-1])) 

    fil_n = fil_n + neg_lit # negation of  last literal added
    
    ord_list.append((fil+".proof", fil_n+".proof", path+"/"))
    temp.sort(key=sorting_key)
  
  return ord_list
     
def write_proof(f, proof):
  for lemma in proof:
    f.write(lemma)


if __name__ == "__main__":
  
  if len(sys.argv) != 2:
    print("Usage: python3 run.py path/to/proof/files")
    print("Proof files must have extension .proof")
    sys.exit(0)
  
  path = sys.argv[1]
  path = path if path[-1] == "/" else path+"/"
  files = glob.glob(path+"*.proof")

  print("Making directory temp-work")
  
  if os.path.exists("./temp-work"):
    shutil.rmtree("./temp-work")

  os.mkdir("./temp-work")
  
  for f in files:
    shutil.copy(f, "./temp-work/")
  
  files = glob.glob("./temp-work/*.proof")

  if files is None:
    print("Proof files not found")
    print("Proof files must have extension .proof")
    sys.exit(0)

  ordered_proof = order_proofs(files)
  '''
  for o in ordered_proof:
    print(o)
  '''
  #print(ordered_proof)
  #sys.exit()
  for tup in ordered_proof:
    #read proofs
    proof_file1 = tup[0]
    proof_file2 = tup[1]
    path = tup[2]
    decision_lits = proof_file1[:-6].split("_")
    decision_lit = decision_lits[-1] if decision_lits[-1][0]!="n" else "-" + decision_lits[-1][1:]
    if len(decision_lits) > 1:
      proof_out_file = "_".join(decision_lits[:-1]) + ".proof"
    else:
      proof_out_file = "final.proof"
    #print(proof_out_file)
    temp_1 = []
    temp_2 = []
    proof_1 = []
    proof_2 = []
    proof_out = []
    with open(path+proof_file1,"r") as f:
      temp_1 = f.readlines()

    with open(path+proof_file2,"r") as f:
      temp_2 = f.readlines()
    
    # delete deletion clauses
    for l in temp_1:
      if l[0] != "d":
        proof_1.append(l)
    
    for l in temp_2:
      if l[0] != "d":
        proof_2.append(l)
    #print(proof_file1)
    #print(proof_1)
    #print(proof_2)
    #print(decision_lit)
    #proof_1 = [ l if l[0]!="d" for l in proof_1]
    #proof_2 = [ l in l[0]!="d" for l in proof_2]

    proof_out = combine_proofs(proof_1, proof_2, decision_lit)
    #print(proof_out)
    #sys.exit()
    with open(path+proof_out_file,"w") as f:
      write_proof(f, proof_out)

