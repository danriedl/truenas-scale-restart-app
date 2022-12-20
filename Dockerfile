FROM python:3.9-bullseye
LABEL org.opencontainers.image.authors="daniel.riedl@bmw.de"
LABEL org.opencontainers.image.source="https://github.com/danriedl/truenas-scale-restart-app"
WORKDIR /app
RUN git clone https://github.com/truenas/middleware
WORKDIR /app/middleware/src/middlewared
RUN pip install babel ws4py flask
RUN python setup.py install
WORKDIR /app
ADD app.py /app/
ENTRYPOINT [ "python",  "app.py"]