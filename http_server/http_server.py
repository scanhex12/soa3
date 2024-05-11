from flask import Flask, request, make_response
import json
import requests
import sqlite3
from flask import Flask, request, make_response
import json
from flask import Flask, request, jsonify
import grpc
import posts_pb2
import posts_pb2_grpc

from settings import *

def update_data(login, data):
    data['login'] = login
    response = requests.post(f'http://database:{HTTP_DATABASE_PORT_1}/data/add', data=json.dumps(data))
    return response.status_code


app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def signup():
    body = json.loads(request.data)
    login = body['login']
    password = body['password']
    metadata = {
        'firstName': body.get('firstName'),
        'lastName': body.get('lastName'),
        'birthDate': body.get('birthDate'),
        'mail': body.get('mail'),
        'phoneNumber': body.get('phoneNumber')
    }
        
    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    if response.status_code == 200:
        return make_response('User already exists\n', 403)

    requests.post(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login, 'password': password}))
        
    update_data(login, metadata)

    return make_response('Successful registration\n', 200)

@app.route('/login', methods=['POST'])
def login():
    body = json.loads(request.data)
    login = body['login']
    password = body['password']

    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    
    if response.status_code == 403:
        return make_response('User does not exist\n', 401)
    
    stored_password = response.text.strip()
    
    if stored_password != password:
        return make_response('Incorrect password\n', 403)

    response_metadata = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/data', data=json.dumps({'login': login}))
    
    if response_metadata.status_code != 200:
        return make_response('Error retrieving user data\n', 500)
    
    metadata = response_metadata.json()
    return make_response(json.dumps(metadata), 200, {'Content-Type': 'application/json'})

@app.route('/update', methods=['POST'])
def update():
    body = json.loads(request.data)
    login = body['login']
    password = body['password']
        
    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    stored_password = response.text
        
    if stored_password != password:
        return make_response('Incorrect password\n', 403)
        
    metadata = {
        'firstName': body.get('firstName'),
        'lastName': body.get('lastName'),
        'birthDate': body.get('birthDate'),
        'mail': body.get('mail'),
        'phoneNumber': body.get('phoneNumber')
    }
        
    response = update_data(login, metadata)
        
    return make_response(f'Successfully updated user data\n{response}\n', 200)


###############################################################


channel = grpc.insecure_channel(f'grpc_server:{GRPC_PORT_1}')
stub = posts_pb2_grpc.PostServiceStub(channel)

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    print("CREATE POST")
    login = data['login']
    password = data['password']
        
    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    stored_password = response.text
        
    if stored_password != password:
        return make_response('Incorrect password\n', 403)

    response = stub.CreatePost(posts_pb2.CreatePostRequest(
        title=data['title'],
        content=data['content'],
        user_id=login
    ))
    return jsonify({'message': 'Post created', 'post': {'id': response.id}})

@app.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    
    login = data['login']
    password = data['password']
        
    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    stored_password = response.text
        
    if stored_password != password:
        return make_response('Incorrect password\n', 403)

    response = stub.GetPost(posts_pb2.GetPostRequest(
        id=post_id
    ))

    if response.user_id != login:
        return make_response('Access denied\n', 403)

    response = stub.UpdatePost(posts_pb2.UpdatePostRequest(
        id=post_id,
        title=data['title'],
        content=data['content'],
        user_id=login
    ))
    return jsonify({'message': 'Post updated'})

@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    data = request.get_json()

    login = data['login']
    password = data['password']
        
    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    stored_password = response.text
        
    if stored_password != password:
        return make_response('Incorrect password\n', 403)

    response = stub.GetPost(posts_pb2.GetPostRequest(
        id=post_id
    ))

    if response.user_id != login:
        return make_response('Access denied\n', 403)

    response = stub.DeletePost(posts_pb2.DeletePostRequest(
        id=post_id
    ))
    return jsonify({'message': 'Post deleted'})

@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    data = request.get_json()

    login = data['login']
    password = data['password']
        
    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    stored_password = response.text
        
    if stored_password != password:
        return make_response('Incorrect password\n', 403)

    response = stub.GetPost(posts_pb2.GetPostRequest(
        id=post_id
    ))

    if response.user_id != login:
        return make_response('Access denied\n', 403)

    return jsonify({'post': {'id': response.id, 'title': response.title, 'content': response.content, 'user_id': response.user_id}})

@app.route('/posts', methods=['GET'])
def get_posts():
    print("GET POSTS")
    data = request.get_json()
    print("posts ", data)

    login = data['login']
    password = data['password']
        
    response = requests.get(f'http://database:{HTTP_DATABASE_PORT_1}/auth', data=json.dumps({'login': login}))
    stored_password = response.text
        
    if stored_password != password:
        return make_response('Incorrect password\n', 403)
    page = data['page']
    page_size = data['page_size']
        
    posts = []
    print("posts ", page, page_size)
    for response in stub.GetPosts(posts_pb2.GetPostsRequest(page=int(page), page_size=int(page_size))):
        if response.user_id != login:
            return make_response('Access denied\n', 403)
        posts.append({'id': response.id, 'title': response.title, 'content': response.content, 'user_id': response.user_id})
    return jsonify({'posts': posts})


def main():
    app.run(host='0.0.0.0', port=HTTP_PORT_1, debug=True)

if __name__ == "__main__":
    main()