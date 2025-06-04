# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application (e.g., app.py, templates/)
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
