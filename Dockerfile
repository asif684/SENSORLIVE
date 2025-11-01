FROM python:3.10-slim-bookworm

RUN apt update -y && apt install -y awscli
WORKDIR /app
COPY . /app

CMD ["python", "main.py"]
