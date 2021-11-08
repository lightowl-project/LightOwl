from apps.agent.models import Agent
import mongoengine

GRAPH_TYPE_CHOICES: tuple = (
    ("gauge", "gauge"),
    ("time", "time"),
    # ("pie", "pie"),
    ("text", "text")
)


class GeneralDashboardWidget(mongoengine.EmbeddedDocument):
    agent = mongoengine.ReferenceField(Agent)
    x = mongoengine.IntField()
    y = mongoengine.IntField()
    w = mongoengine.IntField()
    h = mongoengine.IntField()


class GeneralDashboard(mongoengine.Document):
    widgets = mongoengine.EmbeddedDocumentListField(GeneralDashboardWidget)


class Dashboard(mongoengine.Document):
    name = mongoengine.StringField()
    agent = mongoengine.ReferenceField(Agent, reverse_delete_rule=mongoengine.CASCADE)


class Widget(mongoengine.Document):
    name = mongoengine.StringField()
    graph_type = mongoengine.StringField(choices=GRAPH_TYPE_CHOICES)
    measurement = mongoengine.StringField()
    field = mongoengine.StringField()
    options: mongoengine.DictField()
    interval = mongoengine.StringField()



class DashboardWidgets(mongoengine.Document):
    dashboard = mongoengine.ReferenceField(Dashboard, reverse_delete_rule=mongoengine.CASCADE)
    widget = mongoengine.ReferenceField(Widget, reverse_delete_rule=mongoengine.CASCADE)

    x = mongoengine.IntField()
    y = mongoengine.IntField()
    w = mongoengine.IntField()
    h = mongoengine.IntField()
    i = mongoengine.IntField()
