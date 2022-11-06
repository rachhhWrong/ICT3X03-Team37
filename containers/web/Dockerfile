FROM tiangolo/uvicorn-gunicorn:python3.9-slim

COPY ./website /app/website
COPY ./main.py /app/main.py
EXPOSE 5000
RUN pip install --no-cache-dir flask_pymongo passlib[bcrypt] pyotp stripe asgiref
