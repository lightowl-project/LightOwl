FROM python:3.10
COPY ./backend/ /app
WORKDIR /app

RUN apt update && apt upgrade -y && apt install -y netcat
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt
RUN pip3 install starlette==0.13.8
RUN mkdir -p /var/log/lightowl/

ENV PYTHONPATH=/app

CMD ["celery", "worker", "-A", "worker", "-l", "info"]
