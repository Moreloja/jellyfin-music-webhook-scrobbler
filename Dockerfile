FROM alpine:latest

RUN apk update && apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY cronjob /etc/crontabs/root

RUN pip install -r requirements.txt

COPY main.py /app/main.py

ENV MONGO_HOST=mongodb \
    MONGO_PORT=27017 \
    MONGO_DB_NAME=moreloja \
    MONGO_USER= \
    MONGO_PASSWORD=

CMD ["crond", "-f"]
