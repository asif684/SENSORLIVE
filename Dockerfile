FROM python:3.8-slim

# Install AWS CLI using pip (simplest & future-proof)
RUN pip install --no-cache-dir awscli

WORKDIR /app
COPY . /app

CMD ["python", "main.py"]
