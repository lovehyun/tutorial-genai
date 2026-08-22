# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY simple_net_server.py /app/

RUN pip install --no-cache-dir "mcp[cli]"

EXPOSE 8000

CMD ["python", "simple_net_server.py"]
