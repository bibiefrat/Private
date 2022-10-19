import re
fhand = open('sample2.txt')
count = 0
for line in fhand:
    line = line.rstrip()
    x = re.findall('[0-9]+', line)
    if len(x) > 0 :
        print x
        for i in x:
            count = count + int(i)
            
print count
S = [x**2 for x in range(10)]
print S
fhand.close()
fhand = open('sample2.txt')
y = sum (map(int,re.findall('[0-9]+', fhand.read())))
print y

