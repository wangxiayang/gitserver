#!/usr/bin/python

import socket
import signal
import sys
import os

HOST = ''   # replace hostname
PORT = 8888 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))

def sigint_handler(signal, frame):
    print 'Interrupted by ctrl+c'
    s.close()

signal.signal(signal.SIGINT, sigint_handler)

s.listen(1) # why 1?

class httpreq:
    def __init__(self, method, url):
        # version of HTTP is ignored
        self.__method = method
        self.__url = url
        self.__headers = {}
    @classmethod
    def fromdata(cls, data):
        lines = data.split('\n')
        reqline = lines[0].split(' ')
        if reqline[0] != 'GET' and reqline[0] != 'PUT':
            print '\33[0;31m[Error]\33[mUnsupported HTTP method:', reqline[0]
            raise Exception('Unsupported HTTP method')
        r = cls(reqline[0], reqline[1])
        # for now just ignore all other lines
        return r
    def getMethod(self):
        return self.__method
    def getUrl(self):
        return self.__url
    def setHeader(self, key, value):
        self.__headers[key] = value

class httpresp:
    def __init__(self, status):
        self.__status = status
        if status == 200:
            self.__desp = 'OK'
        elif status == 404:
            self.__desp = 'Not Found'
        else:
            self.__desp = 'Unsupported'
        self.__headers = {}
    def setBody(self, data):
        self.__body = data
    def getBody(self):
        return self.__body
    def getResp(self):
        r = 'HTTP/1.1 ' + repr(self.__status) + ' ' + self.__desp + '\n'
        r += 'Content-Type: text/html; charset=utf-8\n'
        r += 'Content-Length: ' + repr(len(self.__body)) + '\n'
        r += '\n'
        r += self.__body + '\n'
        return r

def fail(r, s):
    f = open('failure.html', 'r')
    r.setBody(f.read())
    f.close()
    s.send(r.getResp())

while 1:
    try:
        print '\33[0;32mWait for connection...\33[m'
        conn, addr = s.accept()
        #conn.setblocking(0)
    except:
        print 'Exception happened on accept!'
        sys.exit()

    print 'Connected by', addr

    data = conn.recv(1024)
    if not data:
        conn.close()
        continue

    try:
        req = httpreq.fromdata(data)
    except:
        s.close()
        sys.exit()
        
    print '\33[0;33mReceived:\33[m', req.getMethod(), req.getUrl(), '#'
    if req.getUrl() == '/':
        resp = httpresp(200)
        f = open('index.html', 'r')
        resp.setBody(f.read())
        f.close()
        conn.send(resp.getResp())
    elif req.getUrl().find('gitinit.py') != -1:
        reponame = req.getUrl()[22:]
        resp = httpresp(200)
        if os.path.isdir('/git/' + reponame + '.git'):
            # if already exists
            fail(resp, conn)
        else:
            r = os.system('cd /git; git init --bare ' + reponame + '.git')
            if r != 0:
                fail(resp, conn)
            else:
                f = open('success.html', 'r')
                resp.setBody(f.read())
                f.close()
                conn.send(resp.getResp())
    else:
        resp = httpresp(404)
        resp.setBody('<html><title>Not support</title><body>Not found</body></html>')
        conn.send(resp.getResp())
    conn.close()
    print '\33[0;32mConnection end\33[m'
s.close()
