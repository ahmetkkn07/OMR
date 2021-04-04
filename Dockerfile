FROM python:3.9-slim-buster

COPY ./ /home

WORKDIR /home

RUN apt-get update -y \
    && apt-get -y install libgl1-mesa-glx \
    && apt-get install -y 'ffmpeg'\
    'libsm6'\
    'libxext6'

RUN pip3 install -r requirements.txt

CMD ["python3" , "server.py"]

EXPOSE 80/tcp