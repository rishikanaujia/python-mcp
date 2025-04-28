FROM python:3.9-slim

WORKDIR /app

COPY session_manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY session_manager/ /app/

EXPOSE 5000

CMD ["python", "app.py"]
