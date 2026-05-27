FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/data /app/staticfiles /app/media

EXPOSE 8000

CMD ["gunicorn", "iot_monitoring.wsgi:application", "--bind", "0.0.0.0:8000"]
