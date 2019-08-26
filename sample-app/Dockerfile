FROM python:3.6-alpine

RUN apt-get update -y

WORKDIR /app

RUN pip install flask

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]