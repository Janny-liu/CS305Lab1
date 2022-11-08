import json
import os
import random
import string
from typing import *
import config
import mimetypes
from framework import HTTPServer, HTTPRequest, HTTPResponse


def random_string(length=20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def default_handler(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    response.status_code, response.reason = 404, 'Not Found'
    print(f"calling default handler for url {request.request_target}")


def task2_data_handler(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    # TODO: Task 2: Serve static content based on request URL (20%)
    requestTarget = request.request_target
    filename = "." + requestTarget
    try:
        # read the file by binary
        f = open(filename, 'rb')
        # response the status code and reason
        response.status_code, response.reason = 200, 'OK'
        bodydata = f.read()
        # response the Content-Length and Content-Type
        response.add_header("Content-Length", str(len(bodydata)))
        response.add_header("Content-Type", mimetypes.guess_type(requestTarget)[0])
        if request.method == 'GET':
          response.body = bodydata
        elif request.method == 'HEAD':
            response.body=None
        f.close()
    except FileNotFoundError:
        # response the status code and reason
        response.status_code, response.reason = 404, 'Not Found'
        # tell the reason
        print(f"calling task2_data_handler for url {requestTarget}")
    pass


def task3_json_handler(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    # TODO: Task 3: Handle POST Request (20%)
    # response the status code and reason
    response.status_code, response.reason = 200, 'OK'
    if request.method == 'POST':
        binary_data = request.read_message_body()
        obj = json.loads(binary_data)
        # TODO: Task 3: Store data when POST
        print(str(obj))
        # obtain the message which key is "data"
        server.task3_data = str(obj['data'])
        # preserve the response message
        writedata = "{" + f'"data": "{server.task3_data}"' + "}"
        with open('post', 'w') as f:
            f.write(writedata)
        pass
    else:
        # response the other method
        obj = {'data': server.task3_data}
        return_binary = json.dumps(obj).encode()
        # print(return_binary)
        response.add_header("Content-Type", mimetypes.guess_type("json.json")[0])
        response.add_header("Content-Length", str(len(return_binary)))
        if request.method == 'GET':
          response.body = return_binary
        elif request.method == 'HEAD':
            response.body=None
        pass


def task4_url_redirection(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    # TODO: Task 4: HTTP 301 & 302: URL Redirection (10%)
    response.status_code, response.reason = 302, 'Found'
    response.add_header("Location", "http://127.0.0.1:8080/data/index.html")
    pass


def task5_test_html(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    response.status_code, response.reason = 200, 'OK'
    with open("task5.html", "rb") as f:
        response.body = f.read()


def task5_cookie_login(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    # TODO: Task 5: Cookie, Step 1 Login Authorization
    obj = json.loads(request.read_message_body())
    if obj["username"] == 'admin' and obj['password'] == 'admin':
        response.status_code, response.reason = 200, 'OK'
        response.add_header("Set-Cookie", "Authenticated=yes")
        pass
    else:
        response.status_code, response.reason = 403, 'Forbidden'
        pass


def task5_cookie_getimage(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    # TODO: Task 5: Cookie, Step 2 Access Protected Resources
    for head in request.headers:
        if head.name == "Cookie" and head.value == "Authenticated=yes":
            response.status_code, response.reason = 200, 'OK'
            fileName = "data\\test.jpg"
            with open(fileName, 'rb') as f:
                imagedata = f.read()
            response.add_header("Content-Length", str(len(imagedata)))
            response.add_header("Content-Type", mimetypes.guess_type("test.jpg")[0])
            if request.method == 'GET':
                response.body = imagedata
            elif request.method == 'HEAD':
                response.body = None
        else:
            response.status_code, response.reason = 403, 'Forbidden'
    pass


def task5_session_login(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    # TODO: Task 5: Cookie, Step 1 Login Authorization
    obj = json.loads(request.read_message_body())
    if obj["username"] == 'admin' and obj['password'] == 'admin':
        response.status_code, response.reason = 200, 'OK'
        session_key = random_string()
        while session_key in server.session:
            session_key = random_string()
        pass
        #store the seseeion
        server.session = {"SESSION_KEY=": f"{session_key}"}
        response.add_header("Set-Cookie", "SESSION_KEY=" + f"{session_key}")
    else:
        response.status_code, response.reason = 403, 'Forbidden'


def task5_session_getimage(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    # TODO: Task 5: Cookie, Step 2 Access Protected Resources
    for head in request.headers:
        if head.name == "Cookie" and head.value == "SESSION_KEY=" + server.session["SESSION_KEY="]:
            response.status_code, response.reason = 200, 'OK'
            fileName = "data\\test.jpg"
            with open(fileName, 'rb') as f:
                imagedata = f.read()
            response.add_header("Content-Length", str(len(imagedata)))
            response.add_header("Content-Type", mimetypes.guess_type("test.jpg")[0])
            if request.method == 'GET':
                response.body = imagedata
            elif request.method == 'HEAD':
                response.body = None
        else:
            response.status_code, response.reason = 403, 'Forbidden'
    pass


# TODO: Change this to your student ID, otherwise you may lost all of your points
YOUR_STUDENT_ID = 11910737

http_server = HTTPServer(config.LISTEN_PORT)
http_server.register_handler("/", default_handler)
# Register your handler here!
http_server.register_handler("/data", task2_data_handler, allowed_methods=['GET', 'HEAD'])
http_server.register_handler("/post", task3_json_handler, allowed_methods=['GET', 'HEAD', 'POST'])
http_server.register_handler("/redirect", task4_url_redirection, allowed_methods=['GET', 'HEAD'])
# Task 5: Cookie
http_server.register_handler("/api/login", task5_cookie_login, allowed_methods=['POST'])
http_server.register_handler("/api/getimage", task5_cookie_getimage, allowed_methods=['GET', 'HEAD'])
# Task 5: Session
http_server.register_handler("/apiv2/login", task5_session_login, allowed_methods=['POST'])
http_server.register_handler("/apiv2/getimage", task5_session_getimage, allowed_methods=['GET', 'HEAD'])

# Only for browser test
http_server.register_handler("/api/test", task5_test_html, allowed_methods=['GET'])
http_server.register_handler("/apiv2/test", task5_test_html, allowed_methods=['GET'])


def start_server():
    try:
        http_server.run()
    except Exception as e:
        http_server.listen_socket.close()
        print(e)


if __name__ == '__main__':
    start_server()
