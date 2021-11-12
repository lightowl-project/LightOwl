from ..schema import ExecuteQuerySchema
from toolkits.influx import Influx
from typing import Union, List
from config import settings
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class WidgetData:
    def __init__(self, params: Union[List[ExecuteQuerySchema], ExecuteQuerySchema]):
        self.params = params
        self.influx = Influx()

    def _where_clause(self, params) -> str:
        where_sql: list = [f"lightowl_id = '{params.agent_id}'"]
        if params.date_start:
            where_sql.extend([f"(time > '{params.date_start}' AND time < '{params.date_end}')"])

        if params.where:
            where_sql.append(params.where)

        return " AND ".join(where_sql)

    def __agg(self, params):
        try:
            measurement_type = self.influx.get_mapping(params.measurement)[params.field]
            if measurement_type not in ("string",):
                return f"{params.agg}({params.field})"

            return params.field
        except KeyError:
            return f"mean({params.field})"

    def __group_by(self, params):
        tmp_group_by: list = []
        if params.group_by:
            tmp_group_by = [params.group_by]
            
        if params.date_start:
            tmp_group_by.insert(0, f"time({params.interval})")
        
        return ", ".join(tmp_group_by)

    def fetch_timeseries(self, params) -> dict:
        query_sql: str = f"SELECT {self.__agg(params)} as value FROM {params.measurement} WHERE {self._where_clause(params)}"

        group_by: str = self.__group_by(params)
        if len(group_by):
            query_sql = f"{query_sql} GROUP BY {group_by} fill(0)"

        if not params.date_start:
            query_sql = f"{query_sql} LIMIT 1"

        logger.info(query_sql)
        tmp_results = self.influx.execute_simple_query(query_sql)
        return tmp_results.raw

    def fetch_influxdata(self):
        if not isinstance(self.params, list):
            self.params = [ExecuteQuerySchema(**self.params.dict())]

        results = {}
        for params in self.params:
            results[f"{params.agent_id}.{params.measurement}.{params.field}"] = self.fetch_timeseries(params)

        return results