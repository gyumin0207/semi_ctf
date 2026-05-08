FROM python:3.11-slim

WORKDIR /app

RUN pip install flask==3.0.3 --no-cache-dir


COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
