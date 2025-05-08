FROM python:3.10-slim

# Don’t write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# stdout/stderr in real time
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
