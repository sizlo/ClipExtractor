FROM python:3.9-buster

RUN apt-get update && apt-get install ffmpeg -y

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT [ "python", "./clip_extractor.py" ]