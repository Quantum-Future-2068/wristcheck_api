FROM python:3.12-slim-bullseye
WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        musl-dev \
        libmysqlclient-dev \
        && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install supervisor

#RUN apt-get update && \
#    apt-get install -y supervisor

ENTRYPOINT ["/app/start.sh"]
CMD [""]