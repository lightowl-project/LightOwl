from mongoengine import connect, disconnect
from config import settings
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("celery")


def mongo_connect(func):
    """
    Decorotor that handles connection to mongo
    :param func: the function to decorate
    :return:
    """
    def func_with_mongo(*args, **kwargs):
        try:
            try:
                disconnect("default")

                params = {
                    "host": settings.MONGO_URL,
                    "alias": "default"
                }

            except Exception:
                logger.exception("Something wrong occurred while connect/disconnect to mongo : ")
                raise

            try:
                db_client = connect(settings.MONGO_DATABASE, **params)
            except Exception:
                logger.exception("Something wrong occurred while connecting to mongoDB : ")
                raise

            try:
                to_return = func(*args, **kwargs)
                try:
                    db_client.close()
                    return to_return
                except Exception:
                    logger.exception("Couldn't close mongo connection : ")
            except Exception:
                db_client.close()
                logger.exception("Something wrong occurred while executing mongo_connect decorator")

        except Exception:
            logger.error("Cannot setup mongoengine connection")

    return func_with_mongo
