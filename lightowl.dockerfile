FROM node:16-alpine3.12 as build-stage
WORKDIR /app
COPY ./frontend/ .
RUN npm install -g npm@7.20.6
RUN npm install
RUN npm run build:prod

FROM python:3.10
COPY ./backend/ /app
WORKDIR /app
COPY --from=build-stage /app/dist /app/templates

RUN apt update && apt install -y netcat
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt
RUN pip3 install starlette==0.13.8
RUN mkdir -p /var/log/lightowl/
EXPOSE 8000
CMD ["uvicorn main:app --host 0.0.0.0 --port 8000"]