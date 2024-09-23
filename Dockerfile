FROM python:3.8.20-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=core/server.py

RUN rm -f core/store.sqlite3
RUN flask db upgrade -d core/migrations/

CMD ["bash", "run.sh"]
