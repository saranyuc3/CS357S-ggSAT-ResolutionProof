import glob
import sys
import subprocess
import shutil
import os
import time

files = glob.glob("uuf50-218/*.cnf")

#files = files[:200]

depth = "10"


if os.path.exists("./outputs/"):
    shutil.rmtree("./outputs/")
os.mkdir("./outputs/")

for fil in files:
  print(fil)
  name = fil[:-4].split("/")[-1]
  print(name)
  print(fil)
  output_path = "outputs/"+name+"/"
  print(output_path)
  
  proof_file = fil.replace('cnf','proof')
  t3 = time.time()
  result = subprocess.run([ "./checker0", fil, proof_file ], stdout=subprocess.PIPE, universal_newlines=True ) 
  t4 = time.time()
  with open("outputs/"+name+".txt", "w") as f:
    f.write(name)
    f.write(result.stdout)
    f.write("Checking time:{}\n\n".format(t4-t3))

