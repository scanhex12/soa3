import grpc
import requests
from concurrent import futures
import posts_pb2 as posts_pb2
import posts_pb2_grpc as posts_pb2_grpc

from settings import GRPC_PORT_1, GRPC_DATABASE_PORT_1

BASE_URL = f'http://posts_database:{GRPC_DATABASE_PORT_1}'

class PostService(posts_pb2_grpc.PostServiceServicer):
    def CreatePost(self, request, context):
        print("CreatePost")
        url = f'{BASE_URL}/posts'
        data = {
            'title': request.title,
            'content': request.content,
            'user_id': request.user_id
        }
        print("send request")
        response = requests.post(url, json=data)
        post_data = response.json()
        print(post_data)

        return posts_pb2.Post(
            id=str(post_data['id']),
            title=post_data['title'],
            content=post_data['content'],
            user_id=post_data['user_id']
        )

    def UpdatePost(self, request, context):
        url = f'{BASE_URL}/posts/{request.id}'
        data = {
            'title': request.title,
            'content': request.content,
            'user_id': request.user_id
        }
        response = requests.put(url, json=data)
        response_data = response.json()

        return posts_pb2.Post(
            id=str(request.id),
            title=request.title,
            content=request.content,
            user_id=request.user_id
        )

    def DeletePost(self, request, context):
        url = f'{BASE_URL}/posts/{request.id}'
        data = {'user_id': request.user_id}
        response = requests.delete(url, json=data)
        response_data = response.json()

        return posts_pb2.DeletePostResponse(success=response_data.get('success', False))

    def GetPost(self, request, context):
        url = f'{BASE_URL}/posts/{request.id}'
        response = requests.get(url)
        if response.status_code == 200:
            post_data = response.json()
            return posts_pb2.Post(
                id=str(post_data['id']),
                title=post_data['title'],
                content=post_data['content'],
                user_id=post_data['user_id']
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return posts_pb2.Post()

    def GetPosts(self, request, context):
        print("start GetPosts")
        url = f'{BASE_URL}/posts'
        params = {
            'page': request.page,
            'page_size': request.page_size
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            posts_data = response.json()
            for post_data in posts_data:
                print("send ", post_data)
                yield posts_pb2.Post(
                    id=str(post_data['id']),
                    title=post_data['title'],
                    content=post_data['content'],
                    user_id=post_data['user_id']
                )
        else:
            return []

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port(f'[::]:{GRPC_PORT_1}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
