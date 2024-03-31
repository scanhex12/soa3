FROM python:3.8-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY __init__.py .
COPY http_client.py .
COPY http_server.py .
COPY posts_pb2.py .
COPY posts_pb2_grpc.py .
COPY settings.py .


CMD ["python", "-m", "http_server"]