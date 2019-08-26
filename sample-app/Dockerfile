FROM python:3.6-alpine

WORKDIR /app

RUN pip install flask

COPY . /app

ENTRYPOINT [ "python" ]

EXPOSE 5000

CMD [ "app.py" ]