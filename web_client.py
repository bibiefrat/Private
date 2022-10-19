import socket
import time


mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysock.connect(('www.py4inf.com', 80))
mysock.send('''GET /cover.jpg HTTP/1.1
Host: www.py4inf.com
Cache-Control: no-cache
Postman-Token: 88e32da1-1833-de6b-d87a-ba9f879db27c\n\n''')


count = 0
picture = "";
while True:
    data = mysock.recv(5120)
    if ( len(data) < 1 ) : break
    time.sleep(0.25)
    count = count + len(data)
    print len(data),count
    picture = picture + data
mysock.close()

# Look for the end of the header (2 CRLF)
pos = picture.find("\r\n\r\n");
print 'Header length',pos
print picture[:pos]
# Skip past the header and save the picture data
picture = picture[pos+4:]
fhand = open("stuff.jpg", "wb")
fhand.write(picture);
fhand.close()