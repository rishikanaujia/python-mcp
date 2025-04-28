FROM python:3.9-slim

WORKDIR /app

COPY servers/tools_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY servers/tools_server/ /app/

EXPOSE 5003

CMD ["python", "app.py"]
