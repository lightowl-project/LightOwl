import re
import json
import asyncio
import logging
import logging.config
from typing import List
from config import settings
from fastapi import WebSocket
from worker.tasks import parseMessage
from aio_pika import connect_robust, Message, IncomingMessage

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("celery")

class RealTime:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.is_ready = False

    async def setup(self, queue_name: str):
        uri: str = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_URL}:{settings.RABBITMQ_PORT}/"
        self.rmq_conn = await connect_robust(
            uri,
            loop=asyncio.get_running_loop()
        )

        self.channel = await self.rmq_conn.channel()
        self.queue_name = queue_name
        queue = await self.channel.declare_queue(self.queue_name, durable=True)
        await queue.consume(self._notify, no_ack=True)
        self.is_ready = True

    def push(self, msg: str):
        self.channel.default_exchange.publish(
            Message(msg.encode("ascii")),
            routing_key=self.queue_name,
        )

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    def handle_message(self, body: str):
        body = body.decode().split("\n")
        if not body:
            return

        to_be_parsed, alerts = [], []
        for element in body:
            if element == "": continue
            regex = r"(?P<measurement>.*)[\s]*host=(?P<host>.*),lightowl_id=(?P<lightowl_id>[a-z0-9]*)[\s,]*(?P<tags>.*) (?P<time>[0-9]*)"
            result = re.search(regex, element)
            if not result:
                try:
                    alert = json.loads(element)
                    alerts.append(alert)
                    continue
                except json.JSONDecodeError:
                    continue

            result = result.groupdict()
            try:
                if "," in result["measurement"]:
                    result["measurement"] = result["measurement"].split(",")[0]

                measurement = result["measurement"]
                host = result["host"]
                agent_id = result['lightowl_id']
                tmp_tags = result["tags"]
                date = result["time"]
            except KeyError as err:
                print(result)
                print("err", err)
                continue

            tags: dict = {}
            tmp_tags = tmp_tags.replace("i,", ",")
            if tmp_tags[-1] == "i":
                tmp_tags = tmp_tags[:-1]

            for tmp in tmp_tags.split(","):
                try:
                    k, v = tmp.split("=")
                except ValueError:
                    continue

                tags[k] = v
            
            to_be_parsed.append({
                "measurement": measurement,
                "agent_id": agent_id,
                "host": host,
                "tags": tags,
                "date": date
            })


        return to_be_parsed, alerts

    async def _notify(self, message: IncomingMessage):
        living_connections = []
        to_be_parsed, alerts = self.handle_message(message.body)

        if len(to_be_parsed) > 0:
            parseMessage.apply_async([json.dumps(to_be_parsed)], expires=10)

            while len(self.connections) > 0:
                websocket = self.connections.pop()
                try:
                    await websocket.send_text(json.dumps({"measurements": to_be_parsed}))
                except Exception:
                    continue

                living_connections.append(websocket)

        if len(alerts) > 0:
            while len(self.connections) > 0:
                websocket = self.connections.pop()
                try:
                    await websocket.send_text(json.dumps({"alerts": alerts}))
                except Exception:
                    continue

                living_connections.append(websocket)

        self.connections = living_connections
