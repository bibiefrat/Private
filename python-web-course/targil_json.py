import json
import urllib
input = '''
[
  { "id" : "001",
    "x" : "2",
    "name" : "Chuck"
  } ,
  { "id" : "009",
    "x" : "7",
    "name" : "Chuck"
  } 
]'''

url = raw_input('Enter location: ')
print "Retrieving %s" % str(url)
data = urllib.urlopen(url).read()

info = json.loads(data)
print 'Retrieved %s characters' % str(len(data))
#print json.dumps(info, indent=4)

count = 0
for item in info['comments']:
    #print item['count']
    count += int(item['count'])
print str(count)
#for item in info:
#    print 'Name', item['name']
#    print 'Id', item['id']
#    print 'Attribute', item['x']

