# Optical Mark Recognition

[Türkçe](https://github.com/ahmetkkn07/OMR/blob/main/README-tr.md)

OMR is the process of capturing human-marked data from document forms such as surveys and tests. They are used to read questionnaires, multiple choice examination paper in the form of lines or shaded areas.

# Installation Methods

## Use at your own machine

### Prerequisites

1. Install [Python3](https://www.python.org/).
2. Install pypi packages with running following commands on a terminal

```
pip3 install -r requirements.txt
```

### How to run

1. After the prerequisites, download or clone repository, locate folder in terminal and run following command

```
python3 server.py
```

2. Open [http://localhost:80](http://localhost:80) on your browser and start using.

## Pull From Docker

1. Pull latest image from Dockerhub.

```
docker pull ahmetkkn07/omr:latest
```

2. Run with exposing port.

```
docker run -d -p 80:80 --name omr ahmetkkn07/omr
```

3. Open [http://localhost:80](http://localhost:80) on your browser and start using.

## Build with Dockerfile

1. Clone repository and locate in folder on terminal.
2. Build docker image.

```
docker build . -t omr
```

3. Run image as container

```
docker run -d -p 80:80 --name omr omr
```

4. Open [http://localhost:80](http://localhost:80) on your browser and start using.

# Features

-   Obtain answer key from image
-   Detect correct, wrong, and empty question counts
-   Recognize name fields on papers

# Preview

![](preview.gif)
