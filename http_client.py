import requests
import json
from settings import HTTP_PORT_1

base_url = f'http://localhost:{HTTP_PORT_1}'

def create_post():
    data = {
        'title': 'post_title',
        'content': 'post_content',
        'user_id': 'user123'
    }
    response = requests.post(f'{base_url}/posts', json=data)
    print(response.json())
    return response.json()['post']['id']

def update_post(post_id):
    data = {
        'title': 'new_post_title',
        'content': 'new_post_content',
        'user_id': 'user123'
    }
    response = requests.put(f'{base_url}/posts/{post_id}', json=data)
    print(response.json())

def delete_post(post_id):
    response = requests.delete(f'{base_url}/posts/{post_id}')
    print(response.json())

def get_post(post_id):
    response = requests.get(f'{base_url}/posts/{post_id}')
    print(response.json())

def get_posts(page=1, page_size=1):
    params = {
        'page': page,
        'page_size': page_size
    }
    response = requests.get(f'{base_url}/posts', params=params)
    print(response.json())

if __name__ == '__main__':
    post_id = create_post()

    get_posts(post_id)

    get_post(post_id=post_id)

    update_post(post_id=post_id)

    delete_post(post_id=post_id)