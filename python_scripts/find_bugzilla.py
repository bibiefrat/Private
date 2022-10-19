import re


def find():
    list = []
    r = re.compile('.*BUGZILLA-[0-9]*.*')
    f = open("/tmp/closed_bugs1.txt","r")
    lines = f.readlines()
    for line in lines:
        if r.match(line) != None:
            m = re.search("(BUGZILLA-[0-9]*)", line)
            list.append(m.group(1))
    for i in list:
        print str(i) + ",",
    
   
def main():
    find()            
            
if __name__ == "__main__":
    main()
