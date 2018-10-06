FROM python:3.6

COPY app/ /app

WORKDIR /app

ENV LINE_CHANNEL_SECRET = <YOUR_LINE_CHANNEL_SECRET>

ENV LINE_CHANNEL_ACCESS_TOKEN = <YOUR_LINE_CHANNEL_ACCESS_TOKEN>

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py || python get-pip.py

RUN pip install -r requirements.txt

CMD ["gunicorn", "--certfile", "app/cert.pem", "--keyfile", "app/key.pem", "-b", "0.0.0.0:8000", "app:app"]
