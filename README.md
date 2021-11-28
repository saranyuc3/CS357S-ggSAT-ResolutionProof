ggSAT simulator with proof emission utility  

**usage**: (*from top dir*) python3 ggSAT\_sim.py **\<path\_to\_problem\_file\>** **\<branching\_depth\>** **\<output\_dir\>** **\<p/s\>**   

p - for parallel execution  
s - for sequential execution  
branching_depth - Maximum number of variables the Look-Ahead solver will guess upto a solvable sub-problem.
out_dir - dir to dump clausal and resolution proofs.  

e.g., *python3 ggSAT\_sim.py test/random/random\_ksat.dimacs 5 test/random/random\_ksat\_inst1/ p*
