FROM python:3.9

WORKDIR /DevOps

COPY . /DevOps

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "app.py"]
