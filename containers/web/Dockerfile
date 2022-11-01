FROM tiangolo/meinheld-gunicorn-flask

COPY ./website /app/website
COPY ./main.py /app/main.py

RUN pip install --no-cache-dir flask_pymongo passlib[bcrypt]
