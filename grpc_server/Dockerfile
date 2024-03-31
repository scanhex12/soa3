FROM python:3.8-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY __init__.py .
COPY grpc_client_sample.py .
COPY grpc_server.py .
COPY posts_pb2_grpc.py .
COPY posts_pb2.py .
COPY posts.proto .
COPY settings.py .

#RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. posts.proto

CMD ["python", "-m", "grpc_server"]