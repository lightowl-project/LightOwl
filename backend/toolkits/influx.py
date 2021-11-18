from influxdb import InfluxDBClient, exceptions
from apps.metrics.schema import ChartSchema, LogsSchema
from toolkits.paginate import TableParam
from config import settings
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class Influx:
    def __connect(self):
        self.influx_client: InfluxDBClient = InfluxDBClient(
            settings.INFLUX_URL,
            settings.INFLUX_PORT
        )

        self.influx_client.switch_database(settings.INFLUX_DATABASE)

    def change_retention_policy(self, retention_duration: str):
        self.__connect()

        try:
            self.influx_client.alter_retention_policy(
                "lightowl_retention_policy",
                database="lightowl",
                duration=retention_duration,
                replication=1,
                default=True
            )
        except exceptions.InfluxDBClientError as err:
            if "retention policy not found" in str(err):
                # Create Retention Policy
                self.influx_client.create_retention_policy(
                    "lightowl_retention_policy",
                    database="lightowl",
                    duration=retention_duration,
                    replication=1,
                    default=True
                )
                return

            raise

    def get_measurements(self, agent_id: str = None) -> list:
        query: str = f"SHOW MEASUREMENTS ON {settings.INFLUX_DATABASE}"
        if agent_id:
            query += f" WHERE lightowl_id = '{agent_id}'"

        results = self.execute_simple_query(query)
        measurements: list = [point['name'] for point in results.get_points()]
        return measurements

    def get_mapping(self, measurement: str) -> dict:
        self.__connect()

        mapping: dict = {}
        results = self.execute_simple_query(f"SHOW FIELD KEYS ON {settings.INFLUX_DATABASE} FROM {measurement}")
        for point in results.get_points():
            mapping[point["fieldKey"]] = point["fieldType"]

        return mapping
    
    def get_tags(self, measurement: str) -> list:
        self.__connect()
        tags: list = []

        results = self.execute_simple_query(f"SHOW TAG KEYS ON {settings.INFLUX_DATABASE} FROM {measurement}")
        for point in results.get_points():
            if point["tagKey"] != "lightowl_id":
                tags.append(point["tagKey"])
        
        return tags

    def get_tag_values(self, measurement: str, tag: str) -> list:
        self.__connect()
        values: list = []

        sql: str = f"SHOW TAG VALUES ON {settings.INFLUX_DATABASE} FROM {measurement} WITH key = {tag}"
        results = self.execute_simple_query(sql)
        for point in results.get_points():
            values.append((point['value'], point['value']))
        
        return values
    
    def execute_simple_query(self, query: str):
        self.__connect()
        return self.influx_client.query(query)

    def execute_query(self, select: list, table: str, where: str = "", group_by: str=None):
        self.__connect()
        query: str = f"SELECT {', '.join(select)} FROM {table}"

        if where:
            query: str = f"{query} WHERE {where}"

        if group_by:
            query: str = f"{query} GROUP BY {group_by}"

        return self.influx_client.query(query)
        
    def logs(self, logs_schema: LogsSchema, table_param: TableParam):
        self.__connect()
        time_format: str = "%Y-%m-%d %H:%M:%S"
        where_sql: list = [f"time > '{logs_schema.date_start.strftime(time_format)}'", f"time < '{logs_schema.date_end.strftime(time_format)}'"]

        if logs_schema.agent:
            where_sql.append(f"lightowl_id = '{logs_schema.agent}'")

        query_sql: str = f"SELECT * FROM {logs_schema.measurement} WHERE {' AND '.join(where_sql)}"

        limit: str = f"{table_param.per_page}"
        offset: str = f"{table_param.per_page * table_param.page}"

        sort: list = table_param.sort.split("|")

        mapping_order: dict = {
            "ascending": "ASC",
            "descending": "DESC"
        }

        try:
            order: str = f"{sort[0]} {mapping_order[sort[1].upper()]}"
        except KeyError:
            order: str = "time DESC"

        query_sql = f"{query_sql} ORDER BY {order} LIMIT {limit} OFFSET {offset}"

        logger.debug(query_sql)

        tmp_results = self.execute_simple_query(query_sql)
        result = list(tmp_results.get_points())

        mapping: dict = self.get_mapping(logs_schema.measurement)
        key: str = list(mapping.keys())[0]
        query_total_str: str = f"SELECT count({key}) FROM {logs_schema.measurement} WHERE {' AND '.join(where_sql)}"
        tmp_count = self.execute_simple_query(query_total_str)

        try:
            return result, list(tmp_count.get_points())[0]["count"]
        except IndexError:
            return [], 0        

    def chart(self, chart_schema: ChartSchema):
        self.__connect()
        time_format: str = "%Y-%m-%d %H:%M:%S"
        where_sql: list = [f"time > '{chart_schema.date_start.strftime(time_format)}'", f"time < '{chart_schema.date_end.strftime(time_format)}'"]
        if chart_schema.agent:
            where_sql.append(f"lightowl_id = '{chart_schema.agent}'")

        mapping: dict = self.get_mapping(chart_schema.measurement)

        key: str = list(mapping.keys())[0]
        query_sql: str = f"SELECT count({key}) as count FROM {chart_schema.measurement} WHERE {' AND '.join(where_sql)}"

        group_by: list = [f'time({chart_schema.interval})']
        if chart_schema.group_by:
            group_by.append(chart_schema.group_by)            

        query_sql: str = f"{query_sql} GROUP BY {', '.join(group_by)}"

        logger.debug(query_sql)
        tmp_results = self.execute_simple_query(query_sql)
        return tmp_results.raw
        