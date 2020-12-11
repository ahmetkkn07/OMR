# Optical Mark Recognition

[Türkçe](https://github.com/ahmetkkn07/OMR/blob/main/README-tr.md)

OMR is the process of capturing human-marked data from document forms such as surveys and tests. They are used to read questionnaires, multiple choice examination paper in the form of lines or shaded areas.
## Prerequisites
1. Install [Python](https://www.python.org/).
2. Install pypi packages with running following commands on a terminal
  ```
  pip install -r requirements.txt
  ```
## How to run
After the prerequisites, download or clone repository, locate folder in terminal and run following command
  ```
  python server.py
  ```
Open [http://localhost:5000](http://localhost:5000) on your browser and start using.

## Features
* Obtain answer key from image
* Detect correct, wrong, and empty question counts
* Recognize name fields on papers

## Preview
![](preview.gif)

