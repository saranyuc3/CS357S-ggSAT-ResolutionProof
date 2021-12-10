import glob
import sys
import subprocess
import shutil
import os
import time

files = ['cnfs/random_ksat.dimacs','cnfs/random_ksat_92.dimacs','cnfs/random_ksat_41.dimacs','cnfs/random_ksat_16.dimacs','cnfs/random_ksat_14.dimacs']

#files = files[:250]

depth = "2"


if os.path.exists("./outputs/"):
    shutil.rmtree("./outputs/")
os.mkdir("./outputs/")

for fil in files:
  print(fil)
  name = fil[:-7].split("/")[-1]
  print(name)
  print(fil)
  output_path = "outputs/"+name+"/"
  print(output_path)
  path_json = "cnfs/"+name+"_leaves.json"
  print(path_json)
  subprocess.check_output(["python3", "ggSAT_sim.py", fil, depth, output_path, "p", path_json])
  print('STARTING PROOF GEN') 
  t1 = time.time()
  subprocess.check_output(["python3", "proof_concat.py", output_path, fil])
  t2 = time.time()
  proof_file = fil[:-3]+"proof"
  t3 = time.time()
  result = subprocess.run([ "./checker0", fil, proof_file ], stdout=subprocess.PIPE, universal_newlines=True ) 
  t4 = time.time()
  with open("outputs/"+name+".txt", "w") as f:
    f.write(name)
    f.write(result.stdout)
    f.write("Proof Concat Time:{}\n".format(t2-t1))
    f.write("Checking time:{}\n".format(t4-t3))

