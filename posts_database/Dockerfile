FROM python:3.8-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY posts.db .
COPY settings.py .

ENTRYPOINT ["python", "-m", "main"]
