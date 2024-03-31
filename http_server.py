from flask import Flask, request, jsonify
import grpc
import posts_pb2
import posts_pb2_grpc

from settings import GRPC_PORT_1, HTTP_PORT_1

app = Flask(__name__)

channel = grpc.insecure_channel(f'localhost:{GRPC_PORT_1}')
stub = posts_pb2_grpc.PostServiceStub(channel)

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    response = stub.CreatePost(posts_pb2.CreatePostRequest(
        title=data['title'],
        content=data['content'],
        user_id=data['user_id']
    ))
    return jsonify({'message': 'Post created', 'post': {'id': response.id}})

@app.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    response = stub.UpdatePost(posts_pb2.UpdatePostRequest(
        id=post_id,
        title=data['title'],
        content=data['content'],
        user_id=data['user_id']
    ))
    return jsonify({'message': 'Post updated'})

@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    response = stub.DeletePost(posts_pb2.DeletePostRequest(
        id=post_id
    ))
    return jsonify({'message': 'Post deleted'})

@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    response = stub.GetPost(posts_pb2.GetPostRequest(
        id=post_id
    ))
    return jsonify({'post': {'id': response.id, 'title': response.title, 'content': response.content, 'user_id': response.user_id}})

@app.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    posts = []
    for response in stub.GetPosts(posts_pb2.GetPostsRequest(page=page-1, page_size=page_size)):
        posts.append({'id': response.id, 'title': response.title, 'content': response.content, 'user_id': response.user_id})
    return jsonify({'posts': posts})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=HTTP_PORT_1)
