FROM python:3.12-bullseye
WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install supervisor

ENTRYPOINT ["/app/start.sh"]
CMD [""]