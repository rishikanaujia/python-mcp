FROM python:3.9-slim

WORKDIR /app

COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY client/ /app/

EXPOSE 8080

CMD ["python", "app.py"]
