FROM python:3.12
LABEL authors="Bruce Walker"

WORKDIR /mntp

COPY ./requirements.txt /mntp/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /mntp/requirements.txt

COPY ./app /mntp/app
COPY ./models /mntp/models

ENTRYPOINT ["python", "./app/main.py"]