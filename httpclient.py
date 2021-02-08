#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        host = urlparse(url).hostname
        port = urlparse(url).port
        return host,port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        code = data.split('\n\n')[0].split(" ")[1]
        return code

    def get_headers(self,data):
        headers = data.split('\n\r\n')[0]
        return headers[1:]

    def get_body(self, data):
        body = data.split('\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        path = urlparse(url).path
        if not path:
            path = "/"
        request = f"GET {path} HTTP/1.1\r\n"
        host, port = self.get_host_port(url)
        request += f"Host: {host}\r\n"
        request += f"Accept: */*\r\n"
        request += f"Connection: close\r\n"
        request += f"User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36\r\n\r\n"
        if port == None:
            port = 80
        self.connect(host,port)
        self.sendall(request)
        response = self.recvall(self.socket)
        code = int(self.get_code(response))
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        path = urlparse(url).path
        if not path:
            path = "/"
        request = f"POST {path} HTTP/1.1\r\n"
        data = ""
        if args != None:
            if len(args) == 1:
                for item in args:
                    data = f"{item}={args[item]}"
            else:
                for item in args:
                    value = args[item]
                    data += f"{item}={value}&"
                data = data[:-1]
        host, port = self.get_host_port(url)
        request += f"Host: {host}\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += f"Content-Length: {len(data)}\r\n"
        request += f"Connection: close\r\n\r\n"
        if data:
            request += data
        if port == None:
            port = 80
        self.connect(host,port)
        self.sendall(request)
        response = self.recvall(self.socket)
        code = int(self.get_code(response))
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
