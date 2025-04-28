FROM python:3.9-slim

WORKDIR /app

COPY servers/resources_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY servers/resources_server/ /app/

EXPOSE 5001

CMD ["python", "app.py"]
