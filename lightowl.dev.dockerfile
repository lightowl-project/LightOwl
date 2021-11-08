FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY ./backend/ /app
WORKDIR /app

RUN apt update && apt install -y netcat
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt
RUN pip3 install starlette==0.13.8
RUN mkdir -p /var/log/lightowl/
EXPOSE 8000
CMD ["uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
