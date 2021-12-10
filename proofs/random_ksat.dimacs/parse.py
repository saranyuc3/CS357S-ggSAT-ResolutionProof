import json

with open('tmp.txt','r') as f:
  data = f.read()
data = data.split('\n')[:-1]
out = []
for i in range(len(data)):
  tmp = data[i]
  tmp = tmp.rstrip('.proof')
  tmp = tmp.replace('n','-')
  tmp = tmp.split('_')
  out.append([int(i) for i in tmp])

with open('leaves.json','w') as f:
  json.dump(out,f)
