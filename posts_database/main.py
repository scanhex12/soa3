from flask import Flask, request, jsonify
import sqlite3
from settings import *

app = Flask(__name__)

def create_connection():
    return sqlite3.connect('posts.db')

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            user_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/posts', methods=['POST'])
def create_post():
    print("create_post")
    data = request.get_json()
    print(data)
    title = data['title']
    content = data['content']
    user_id = data['user_id']
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)
    ''', (title, content, user_id))
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': post_id, 'title': title, 'content': content, 'user_id': user_id})

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    title = data['title']
    content = data['content']
    user_id = data['user_id']
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE posts SET title = ?, content = ? WHERE id = ? AND user_id = ?
    ''', (title, content, post_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    data = request.get_json()
    user_id = data['user_id']
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM posts WHERE id = ? AND user_id = ?
    ''', (post_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM posts WHERE id = ?
    ''', (post_id,))
    post = cursor.fetchone()
    conn.close()
    if post:
        return jsonify({'id': post[0], 'title': post[1], 'content': post[2], 'user_id': post[3]})
    else:
        return jsonify({'error': 'Post not found'}), 404

@app.route('/posts', methods=['GET'])
def get_posts():
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', 10))
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM posts WHERE id >= ? AND id < ?
    ''', (page * page_size, (page + 1) * page_size))
    posts = cursor.fetchall()
    conn.close()
    return jsonify([{'id': post[0], 'title': post[1], 'content': post[2], 'user_id': post[3]} for post in posts])

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=GRPC_DATABASE_PORT_1)
