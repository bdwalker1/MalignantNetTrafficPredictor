# MalignantNetTrafficPredictor
### API for predicting whether certain computer network traffic conversations are malignant or benign

This repository has everything you need to deploy a working copy on your own system.
There are two parts to this repository, the API and a web application that
demonstrates the API capability.

## Quickstart
To go straight to an installed version of the demonstration web application, 
visit:

http://mntp-demo.hopto.me

The API was created using FastAPI. To see the available endpoints and a
description of what each endpoint does, visit the API's docs page:

http://mntp-api.hopto.me/docs/

## Install your own deployment

For those familiar with Docker containers, you should have no problem using
the instructions below for installing in your chosen configuration. 
Beginners should be able to follow these instructions to get a working
deployment working on their personal workstation.

**Prerequisites:**
- Git (https://git-scm.com/downloads)
- Docker (https://www.docker.com/products/docker-desktop/)
- Python v3.12

**Steps**
1) Open a terminal window and navigate to a folder where you wish to install the repository.

2) Clone this repository with the following `git` command:

    `git clone https://github.com/bdwalker1/MalignantNetTrafficPredictor.git`

3) Navigate to the API folder:

    `cd ./MalignantNetTrafficPredictor/API`

4) Build and run the API Docker container (Docker engine must be running):

    a) `docker build -t tag-mntp-api .`

    b) `docker run -d --name mntp-api -p 8000:80 tag-mntp-api`

5) Navigate to the demo_page folder:

    `cd ../demo_page`

6) Install the required packages for the web application

    `pip install -r ./requirements.txt`

7) Run the demonstration web application:

    `python.exe app/demo_page.py`

   *Wait for the terminal to say `Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)`*

8) Open a new web browser tab/window and go to http://127.0.0.1/

## Additional Information:

#### The Data:
The data used in developing this API was pulled from the 
Malware Detection in Network Traffic Data project on Kaggle:
https://www.kaggle.com/datasets/agungpambudi/network-malware-detection-connection-analysis/

The specific schemas used for the prediction and training input files for the
API can be found in the `schemas` folder in this repository.

Instructions for how to gather/compile your own network traffic data are beyond
the scope of this repository, but to point you in the general direction
of gathering network traffic data I would encourage you to investigate
WireShark (https://www.wireshark.org/).
