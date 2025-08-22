# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY simple_net_server_http.py /app/

RUN pip install --no-cache-dir "mcp[cli]"

EXPOSE 8888

CMD ["python", "simple_net_server_http.py"]
