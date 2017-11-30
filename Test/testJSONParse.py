import json
from pprint import pprint

fData = open ('ship.json', 'r')
line = fData.readline()
while line:
    print (line, end ='')
    line = fData.readline()
print ()
fData.close()
with open ('ship.json', 'r') as fp:
    data = json.load(fp)
    pprint (data)

print (data['ships'][0]['coordinates'])
# pprint(data)