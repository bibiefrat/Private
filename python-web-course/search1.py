import re
fhand = open('sample1')
count = 0
for line in fhand:
    line = line.rstrip()
    if re.search('From:', line) :
        print line
