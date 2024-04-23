import grpc
from concurrent import futures
import posts_pb2
import posts_pb2_grpc
import sqlite3
import threading

from settings import GRPC_PORT_1, TABLE_NAME

def create_connection():
    return sqlite3.connect('posts.db')

class PostService(posts_pb2_grpc.PostServiceServicer):
    def __init__(self):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                user_id TEXT
            )
        ''')
        print(TABLE_NAME)
        self.conn.commit()

    def get_connection(self):
        if not hasattr(threading.current_thread(), "sqlite_connection"):
            threading.current_thread().sqlite_connection = create_connection()
        return threading.current_thread().sqlite_connection

    def CreatePost(self, request, context):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        query = f'''
            INSERT INTO {TABLE_NAME} (title, content, user_id) VALUES ("{request.title}", "{request.content}", "{request.user_id}")
        '''
        self.cursor.execute(query)
        self.conn.commit()
        res = self.cursor.lastrowid
        return posts_pb2.Post(id=str(res), title=request.title, content=request.content, user_id=request.user_id)

    def UpdatePost(self, request, context):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        query = f'''
            UPDATE {TABLE_NAME} SET title="{request.title}", content="{request.content}" WHERE id={int(request.id)} AND user_id="{request.user_id}"
        '''
        print(query)
        self.cursor.execute(query)
        self.conn.commit()
        return posts_pb2.Post(id=str(request.id), title=request.title, content=request.content, user_id=request.user_id)

    def DeletePost(self, request, context):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()

        query = f'''
            DELETE FROM {TABLE_NAME} WHERE id={int(request.id)} AND user_id="{request.user_id}"
        '''
        self.cursor.execute(query)
        self.conn.commit()
        return posts_pb2.DeletePostResponse(success=True)

    def GetPost(self, request, context):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()

        query = f'''
            SELECT * FROM {TABLE_NAME}
        '''
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result:
            return posts_pb2.Post(id=str(result[0]), title=result[1], content=result[2], user_id=result[3])
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return posts_pb2.Post()

    def GetPosts(self, request, context):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()

        query = f'''
            SELECT * FROM {TABLE_NAME} WHERE id>={request.page} AND id<{request.page + request.page_size}
        '''
        print(query)
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            yield posts_pb2.Post(id=str(row[0]), title=row[1], content=row[2], user_id=row[3])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port(f'[::]:{GRPC_PORT_1}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()