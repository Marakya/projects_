FROM python:3.8

WORKDIR /Cloud_app

COPY . /Cloud_app

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "app.py"]
