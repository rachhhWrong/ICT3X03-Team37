FROM python:3.10
COPY .  /ICT3X03-Team37
WORKDIR /ICT3X03-Team37
RUN pip install -r requirements.txt
EXPOSE  3000
CMD ["python3", "main.py"]