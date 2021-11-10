from apps.input.models import Input
from copy import deepcopy
import jinja2


class InvalidJinja(Exception):
    def __init__(self, message):
        self.message = message

    def errors(self):
        return {
            "error": self.message
        }


class Plugin:
    def __init__(self, input, **kwargs):
        if isinstance(input, dict):
            config: dict = input["config"]
        else:
            config: dict = input.config

        input.config = self.SCHEMA(**config)
        self.plugin_obj = input

    def generate_conf(self, agent=None):
        with open(self.CONFIG_FILE, 'r') as f:
            config = f.read()

        j2_template = jinja2.Template(config)

        plugin_config: dict = deepcopy(dict(self.plugin_obj.config))
        return j2_template.render(plugin_config)

    def save(self, agent):
        input_obj = Input(plugin_name=self.plugin_obj.plugin_name, config=self.plugin_obj.config.dict(), agent=agent)
        input_obj.save()

        # plugin: Plugin = input_obj.get_plugin()
        # config: str = plugin.generate_conf()

        # with open(f"/etc/telegraf/telegraf.d/{input_obj.pk}.conf", 'w') as f:
        #     f.write(config)

        # client = docker.from_env()
        # telegraf_docker = client.containers.get("supervision_telegraf_1")
        # telegraf_docker.restart()
