FROM python:2.7-alpine

RUN mkdir -p /src/app

EXPOSE '8008'

ADD . /src/app

RUN cd /src/app \
     && pip install -e .

WORKDIR /src/app/example

RUN python manage.py migrate \
     && python manage.py loaddata fixtures.json

CMD ["python", "manage.py", "runserver", "0.0.0.0:8008"]