#!/usr/bin/python3
from sys import exit
from socket import *
from threading import Thread
from time import strftime
import time
import os
import mimetypes
import csv
import urllib
import filecmp
import shutil
import os
import stat

print('---------------Server is up and running at the port number 8080------------------')


class Error(Exception):
    pass


class MNA(Exception):
    # Raised when the PUT/ DELETE Method is used and the admin flag is not zero
    pass


# This method takes the client request and extracts the relavant headers into variables.
def parseRequest(client_input):
    global version
    try:
        req = client_input.strip().splitlines()
        method = ''
        path = ''
        version = ''
        host_name = ''

        # First line of the request header
        line1 = req[0].split()

        method = line1[0]
        # If no path is given set default path as 'index.html'
        if line1[1] == "/":
            path = "index.html"

        # If request is made for directory then return index.html in that directory.
        elif line1[1].endswith("/"):
            if line1[1].startswith("/"):
                line1[1] = line1[1][1:]
            temp = line1[1]
            path = temp + "index.html"

        # Handles GET parameters	
        elif line1[1].find("?") != -1 and method == "GET":
            param_index = line1[1].find("?")
            path = line1[1][1:param_index]
            if path.endswith("/"):
                path = path + "index.html"
            params = line1[1][param_index + 1:]
            var = []
            # Handle Params
            # Storing parameters in csv file on server side
            with open('GET_Parameters.csv', 'w') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                # Multi Parameter
                if params.find("&") != -1:
                    params_list = params.split('&')
                    for param in params_list:
                        var = param.split("=")
                        key = urllib.parse.unquote_plus(
                            var[0])  # Urllib.parse is used for parsing the encoded URL sent by the client
                        value = urllib.parse.unquote_plus(var[1])
                        filewriter.writerow([key, value])
                    # Single Parameter
                else:
                    var = params.split("=")
                    key = urllib.parse.unquote_plus(
                        var[0])  # Urllib.parse is used for parsing the encoded URL sent by the client
                    value = urllib.parse.unquote_plus(var[1])
                    filewriter.writerow([key, value])


        else:
            path = line1[1]
            if path.startswith('/'):
                path = path[1:]

        # Throws error if path doesn't exist.
        if method != "PUT":
            file = open(path, 'rb')

        version = line1[2]
        i = 1
        # Second line of the request header
        if version == "HTTP/1.1":
            line2 = req[1].split(':')
            host_name = line2[1].strip()
            i += 1
        # The headers of the first line contains the method, path of the file and the HTTP protocol and the second 
        # line contains HOST. Now accepting other headers 

        req_headers = dict([("Method", method), ("Path", path), ("Version", version), ("Host", host_name)])
        line = ''
        while i < len(req) - 1:
            if req[i] == '':
                i += 1
                break
            line = req[i].split(':')
            key = line[0]
            value = line[1]
            req_headers[key] = value
            i += 1

        if len(req) > i and method == "POST":
            if req[i].find("=") == -1:
                line = req[i].split(':')
                key = line[0]
                value = line[1]
                req_headers[key] = value
                i += 1

            else:
                # Handle Params
                # Storing parameters in csv file on server side
                with open('Post_Parameters.csv', 'w') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    var = params = []
                    # Multi Parameter
                    if req[i].find("&") != -1:
                        params = req[i].split('&')
                        for param in params:
                            var = param.split("=")
                            key = urllib.parse.unquote_plus(
                                var[0])  # Urllib.parse is used for parsing the encoded URL sent by the client
                            value = urllib.parse.unquote_plus(var[1])
                            filewriter.writerow([key, value])
                        # Single Parameter
                    else:
                        var = req[i].split("=")
                        key = urllib.parse.unquote_plus(
                            var[0])  # Urllib.parse is used for parsing the encoded URL sent by the client
                        value = urllib.parse.unquote_plus(var[1])
                        filewriter.writerow([key, value])

        if (method == "PUT" or method == "DELETE") and adminFlag == 0:
            # Raises MNA Exception
            raise MNA

        if method == "PUT":
            # Stores file in the string file-put. This will be a text file because it has to be a part of the request
            # body
            fileput = ''
            while i < len(req):
                fileput = fileput + req[i] + '\n'
                i = i + 1

            req_headers["File"] = fileput

        return req_headers


    except:
        # In case of an error, response headers will be returned
        date = time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
        server_name = 'rrb/1.0.0 (Ubuntu)'
        connection = ''
        content_type = 'text/html; charset=iso-8859-1'

        if version == '':
            version = 'HTTP/1.1'

        if method == "":
            method = "GET"

        headers = dict(
            [('Date', date), ('Server', server_name), ('Connection', connection), ('Content-Type', content_type),
             ('Version', version), ("Method", method)])

        # Handle 400: Bad Request
        if ((method != "GET" or method != "POST" or method != "HEAD" or method != "OPTIONS") or (
                version != "HTTP/1.1" or version != "HTTP/1.0") or (version == "HTTP/1.1" and host_name == "")):
            headers["Error"] = 400

        # Handle 403: Forbidden
        if os.path.isfile(path):
            if os.access(path, os.R_OK):
                pass
            else:
                headers["Error"] = 403

        # Handle Error 404: Not Found
        if os.path.isfile(path) == False and path != "" and version != "":
            headers["Error"] = 404

        # Handle Error 405: Method Not Allowed
        if ((method == "PUT" or method == "DELETE") and adminFlag == 0) and (path != "" and version != ""):
            headers["Error"] = 405

        return headers


def processMethod(req_headers):
    version = req_headers["Version"]
    method = req_headers["Method"]
    server_input = ""
    date = time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
    # Handle 501: Method Not Implemented
    if ((method.upper() == "GET" and method != "GET") or (method.upper() == "POST" and method != "POST") or (
            method.upper() == "PUT" and method != "PUT") or (method.upper() == "POST" and method != "POST") or (
            method.upper() == "HEAD" and method != "HEAD") or (method.upper() == "OPTIONS" and method != "OPTIONS") or (
            method.upper() == "DELETE" and method != "DELETE") or (method == "CONNECT") or (method == "TRACE") or (
            method == "PATCH")):
        req_headers["Error"] = 501

    error = req_headers.get("Error")
    file = None
    # Checking if an error occured when a HTTP request was processed.
    if error:
        if error == 400:
            status_line = version + " 400 Bad Request"
            file = open('Error/400.html', 'rb')
        if error == 403:
            status_line = version + " 403 Forbidden"
            file = open('Error/403.html', 'rb')
        if error == 404:
            status_line = version + " 404 Not Found"
            file = open('Error/404.html', 'rb')
        if error == 405:
            status_line = version + " 405 Method Not Allowed"
            file = open('Error/405.html', 'rb')
        if error == 501:
            status_line = version + " 501 Method Not Implemented"
            req_headers = dict([('Date', date), ('Server', 'rrb/1.0.0 (Ubuntu)'), ('Connection', 'close'),
                                ('Content-Type', 'text/html; charset=iso-8859-1'),
                                ("Allow", "POST, OPTIONS, HEAD, GET"), ("Error", 501), ("Method", method),
                                ("Version", version)])

            if adminFlag == 1:
                req_headers["Allow"] = "POST, OPTIONS, HEAD, GET, PUT, DELETE"
            file = open('Error/501.html', 'rb')

        # Method that logs error into errorLog file
        errorLog(date, status_line)

        req_headers.pop("Error")
        req_headers.pop("Method")
        req_headers.pop("Version")

        headers = '\n'.join("{0}: {1}".format(key, val) for (key, val) in req_headers.items())

        if method == "HEAD":
            server_input = status_line + '\n' + headers + '\n' + '\n'
        else:
            server_input = status_line + '\n' + headers + '\n' + '\n'

        return server_input, file

    # Request Header Dictionary
    path = req_headers["Path"]
    # Response
    status_line = version + " 200 OK"
    if method != "PUT":
        last_modified = time.ctime(os.path.getmtime(path))
        length = os.path.getsize(path)
        content_type = (mimetypes.MimeTypes().guess_type(path)[0])
    connection = 'Keep-Alive'

    # GET
    if method == "GET":

        # Conditional GET
        if req_headers.get("If-Modified-Since"):
            modified_date = req_headers.get("If-Modified-Since")[5:]
            last_modified_date = last_modified[4:]
            modified_date_list = modified_date.split()
            last_modified_date_list = last_modified_date.split()

            status_line = version + " 200 OK"
            if int(last_modified_date_list[3]) <= int(modified_date_list[2]):
                if int(last_modified_date_list[3]) == int(modified_date_list[2]):
                    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    if months.index(last_modified_date_list[0]) <= months.index(modified_date_list[1]):
                        if months.index(last_modified_date_list[0]) == months.index(modified_date_list[1]):
                            if int(last_modified_date_list[1]) < int(modified_date_list[0]):
                                pass
                            else:
                                status_line = version + " 304 Not Modified"
                                headers = dict([("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date)])
                                server_input = status_line + '\n' + '\n'.join(
                                    "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'
                                return server_input, None
                    else:
                        status_line = version + " 304 Not Modified"
                        headers = dict([("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date)])
                        server_input = status_line + '\n' + '\n'.join(
                            "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'
                        return server_input, None
            else:
                status_line = version + " 304 Not Modified"
                headers = dict([("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date)])
                server_input = status_line + '\n' + '\n'.join(
                    "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'
                return server_input, None

        file = open(path, 'rb')

        # Flattens dictionary into string and adds data to it	  
        headers = dict([("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date), ("Last-Modified", last_modified),
                        ("Accept-Ranges", "bytes"), ("Content-Length", length), ("Connection", connection),
                        ("Content-Type", content_type)])

        server_input = status_line + '\n' + '\n'.join(
            "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'

        # OPTIONS
    if method == "OPTIONS":
        headers = dict([("Allow", "OPTIONS, GET, HEAD, POST"), ("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date),
                        ("Last-Modified", last_modified), ('Connection', connection), ("Content-Length", 0)])
        if adminFlag == 1:
            headers["Allow"] = "POST, OPTIONS, HEAD, GET, PUT, DELETE"
        server_input = '\n'.join("{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'
        file = None

    # HEAD	
    if method == "HEAD":
        headers = dict([('Server', 'rrb/1.0.0 (Ubuntu)'), ('Date', date), ('Last-Modified', last_modified),
                        ('Accept-Ranges', 'bytes'), ('Content-Length', length), ('Connection', connection),
                        ('Content-Type', content_type)])
        server_input = status_line + '\n' + '\n'.join(
            "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'
        file = None

    # POST
    if method == "POST":
        if os.path.isfile(path):
            if os.access(path, os.R_OK):
                file = open(path, 'rb')

        # Flattens dictionary into string and adds data to it	  
        headers = dict([("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date), ("Last-Modified", last_modified),
                        ("Accept-Ranges", "bytes"), ("Content-Length", length), ("Connection", connection),
                        ("Content-Type", content_type)])

        server_input = status_line + '\n' + '\n'.join(
            "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'

    # PUT	
    if method == "PUT":

        file = None

        # Retrieve file from the client side
        filedata = req_headers["File"]

        index = path.rfind('/')
        if index != -1:
            file_path = path[0:index + 1]
            file_name = path[index + 1:]
        else:
            file_path = ''
            file_name = path

        print(file_path)
        # Create a copy of the file on server side
        with open("copy", 'w') as f:
            f.write(filedata)
        f.close()

        # Equivalent to chmod 777 to copy
        os.chmod("copy", stat.S_IRWXU)

        # Copy the file accordingly
        if os.path.isfile(path):
            if filecmp.cmp(path, "copy"):
                status_line = version + " 204 No Content"
            else:
                # 200 OK already set
                os.remove(path)
                if file_path != '':
                    shutil.move("copy", file_path)
                os.rename(file_path + "copy", path)

        else:
            status_line = version + " 201 Created"
            if file_path != '':
                shutil.move("copy", file_path)
            os.rename(file_path + "copy", path)

        content_location = "/" + path
        headers = dict([("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date), ("Content-Location", content_location),
                        ("Connection", "close")])
        server_input = status_line + '\n' + '\n'.join(
            "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'

    # DELETE
    if method == "DELETE":
        file = None
        headers = dict([("Server", "rrb/1.0.0 (Ubuntu)"), ("Date", date), ("Connection", "close")])
        status_line = version + " 200 OK"
        server_input = status_line + '\n' + '\n'.join(
            "{0}: {1}".format(key, val) for (key, val) in headers.items()) + '\n' + '\n'

        if os.path.isfile(path):
            os.remove(path)
    return server_input, file


def errorLog(date, status_line):
    Message = date + " " + status_line
    appendFile = open("errorLog", "a+")
    appendFile.write(Message)
    appendFile.write('\n\n')
    appendFile.close()


def serverThread(connectionSocket, addr):
    print("New Connection Established with Client {}".format(addr[1]))
    while True:
        client_input = connectionSocket.recv(1024).decode()
        print("Client {}:\n".format(addr[1]), client_input)

        if client_input.lower() == "quit":
            break

        # Request is sent by the client to the server which is parsed here
        req_headers = parseRequest(client_input)

        print("Server:")
        server_input, myFile = processMethod(req_headers)
        print(server_input)

        # Send input from the requested file
        connectionSocket.send(server_input.encode())
        if myFile is not None:
            data = myFile.read()  # data is binary data
            try:
                print(data.decode('ascii'))  # Decoding done to convert byte to string to print on the screen
            except:
                print("File sent to receiver...")
            connectionSocket.sendfile(myFile)
            myFile.close()

    connectionSocket.close()


if __name__ == '__main__':
    try:
        threads = []

        f = open("dev.conf", "r")
        config_variables = f.read()

        l = config_variables.split('\n')
        config = dict([])
        for i in range(len(l)):
            if (l[i] != ''):
                temp = l[i].split()
                key = temp[0]
                value = temp[1]
                config[key] = value
        adminFlag = int(config['adminFlag'])
        serverPort = 8080
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(int(config['MaxKeepAliveRequests']))
        serverRoot = config['serverRoot']
        logfile = config['ErrorLog']
        while True:
            connectionSocket, addr = serverSocket.accept()
            t = Thread(target=serverThread, args=(connectionSocket, addr))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        serverSocket.close()
    except KeyboardInterrupt:
        print("\nSayonara")
        exit()
