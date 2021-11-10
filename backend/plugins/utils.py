def get_mapping() -> dict:
    from .elasticsearch import Elasticsearch
    from .postgresql import Postgresql
    from .http_response import HTTPResponse
    from .mongodb import MongoDB
    from .proxmox import Proxmox
    from .apache import Apache
    from .fail2ban import Fail2ban
    from .haproxy import Haproxy
    from .system import System
    from .docker import Docker
    from .redis import Redis
    from .ping import Ping


    return {
        "ping": Ping,
        "redis": Redis,
        "system": System,
        "docker": Docker,
        "haproxy": Haproxy,
        "mongodb": MongoDB,
        "proxmox": Proxmox,
        "apache": Apache,
        "fail2ban": Fail2ban,
        "postgresql": Postgresql,
        "httpresponse": HTTPResponse,
        "elasticsearch": Elasticsearch
    }


class PluginDoesNotExist(Exception):
    pass


def get_plugin(plugin_name: str):
    try:
        return get_mapping()[plugin_name.lower()]
    except KeyError:
        raise PluginDoesNotExist()


def get_schema(plugin_name: str):
    try:
        plugin = get_mapping()[plugin_name.lower()]
        return plugin.SCHEMA
    except KeyError:
        raise PluginDoesNotExist


def get_plugin_config(plugin):
    tmp = plugin.SCHEMA.schema()

    config = plugin.SCHEMA.Config
    tmp["color"] = config.color

    if getattr(config, "img", None):
        tmp["img"] = getattr(config, "img", None)
        tmp["img_size"] = getattr(config, "img_size", "70px")
    else:
        tmp["icon"] = getattr(config, "icon", None)

    return tmp


def plugins_list():
    plugins: list = []
    for key, classe in get_mapping().items():
        tmp = get_plugin_config(classe)
        tmp["key"] = key
        plugins.append(tmp)
        
    return plugins
    