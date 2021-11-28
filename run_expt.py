import glob
import sys
import subprocess
import shutil
import os

files = glob.glob("./test/uuf50-218/*")

files = files[:10]
files = ["./test/uuf50-218/uuf50-0102.cnf"]

depth = "5"

f = open("output-log.txt", "w")
for fil in files:
  print(fil)
  name = fil[:-4].split("/")[-1]
  print(name)
  output_path = "./outputs/"+name+"/"
  if os.path.exists("./outputs/"):
    shutil.rmtree("./outputs/")
  os.mkdir("./outputs/")

  subprocess.run(["python3", "ggSAT_sim.py", fil, depth, output_path, "p"])
  subprocess.run(["python3", "proof_concat.py", output_path])
  #result = subprocess.run(["time", "./drat-trim", fil, "./temp-work/final.proof"],stdout=subprocess.PIPE, universal_newlines=True ) 
  #f.write(name)
  #f.write(result.stdout)

f.close()
