FROM python:3.8-slim

WORKDIR /main_service/database
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY database.py .
COPY database.db .
COPY settings.py .

ENTRYPOINT ["python", "-m", "database"]
