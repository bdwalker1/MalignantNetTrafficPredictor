FROM python:3.12
LABEL authors="Bruce Walker"

WORKDIR /demo_page

COPY ./requirements.txt /demo_page/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /demo_page/requirements.txt

COPY ./app /demo_page/app
COPY ./webpage /demo_page/webpage
RUN mkdir -p ./models_user

ENTRYPOINT ["python", "./app/demo_page.py"]