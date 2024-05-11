import requests
import json
from settings import *

base_url = f'http://127.0.0.1:{HTTP_PORT_1}'

def create_user():
    data = {
        "login" : "test_user",
        "password" : "5612347",
        'firstName': 'firstName',
        'lastName': 'lastName',
        'birthDate': 'birthDate',
        'mail': 'mail',
        'phoneNumber': 'phoneNumber'

    }
    response = requests.post(f'{base_url}/signup', json=data)
    print(response)

def create_user2():
    data = {
        "login" : "test_user1",
        "password" : "5612347",
        'firstName': 'firstName',
        'lastName': 'lastName',
        'birthDate': 'birthDate',
        'mail': 'mail',
        'phoneNumber': 'phoneNumber'
    }
    response = requests.post(f'{base_url}/signup', json=data)
    print(response)

def create_post():
    data = {
        "login" : "test_user",
        "password" : "5612347",
        'title': 'post_title',
        'content': 'post_content',
    }
    response = requests.post(f'{base_url}/posts', json=data)
    print(response)
    return response.json()['post']['id']

def update_post(post_id):
    data = {
        "login" : "test_user",
        "password" : "5612347",
        'title': 'new_post_title',
        'content': 'new_post_content',
    }
    response = requests.put(f'{base_url}/posts/{post_id}', json=data)
    print(response)

def delete_post(post_id):
    data = {
        "login" : "test_user1",
        "password" : "5612347",
    }
    response = requests.delete(f'{base_url}/posts/{post_id}', json=data)
    print(response)

def get_post(post_id):
    data = {
        "login" : "test_user",
        "password" : "5612347",
    }

    response = requests.get(f'{base_url}/posts/{post_id}', json=data)
    print(response.json())

def get_posts(page=1, page_size=1):
    params = {
        "login" : "test_user",
        "password" : "5612347",
        'page': page,
        'page_size': page_size
    }
    response = requests.get(f'{base_url}/posts', json=params)
    print(response)

if __name__ == '__main__':
    create_user()

    create_user2()
    post_id = create_post()

    get_posts(post_id)
    
    get_post(post_id=post_id)

    update_post(post_id=post_id)

    delete_post(post_id=post_id)