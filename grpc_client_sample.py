import grpc
import posts_pb2
import posts_pb2_grpc

from settings import GRPC_PORT_1

def run():
    with grpc.insecure_channel(f'localhost:{GRPC_PORT_1}') as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)

        post = stub.CreatePost(posts_pb2.CreatePostRequest(
            title='title_sample',
            content='content_sample',
            user_id='user123'
        ))
        print(post)

        post_id = post.id
        fetched_post = stub.GetPost(posts_pb2.GetPostRequest(id=post_id))
        print(fetched_post)

        updated_post = stub.UpdatePost(posts_pb2.UpdatePostRequest(
            id=post_id,
            title='new_title_sample',
            content='new_content_sample',
            user_id='user123'
        ))
        print(updated_post)

        post = stub.CreatePost(posts_pb2.CreatePostRequest(
            title='title_sample_2',
            content='content_sample_2',
            user_id='user123'
        ))
        print(post)

        posts_page = stub.GetPosts(posts_pb2.GetPostsRequest(page=1, page_size=2, user_id='user123'))
        for fetched_post in posts_page:
            print(fetched_post)

        delete_response = stub.DeletePost(posts_pb2.DeletePostRequest(id=post_id, user_id='user123'))
        print(delete_response)


run()