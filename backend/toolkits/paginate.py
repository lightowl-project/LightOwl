from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from config import settings
from typing import Union
import logging.config
import logging
import math


logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class TableParam(BaseModel):
    sort: str = "name|desc"
    page: int = 1
    per_page: int = 10
    search: str = ""

    
def construct_search(schema, search, query=None):
    if search:
        fields: dict = schema.schema()["properties"]
        or_clause: list = []
        for field, type_ in fields.items():
            if field == "_id": continue

            where_clause: dict = {}
            if type_["type"] not in ("integer", "string", "float", "array"): continue
            if type_["type"] == "integer":
                try:
                    where_clause[field] = int(search)
                except ValueError:
                    continue
            elif type_["type"] == "double":
                try:
                    where_clause[field] = float(search)
                except ValueError:
                    continue
            elif type_["type"] == "array":
                where_clause[field] = {"$in": [search]}
            else:
                where_clause[field] = {"$regex": f".*{search}.*", "$options": "i"}

            or_clause.append(where_clause)

        s: dict = {
            "$or": or_clause
        }

        if not query:
            query: dict = {"$match": s}
        else:
            try:
                query["$and"].append({"$or": s["$or"]})
            except KeyError:
                query["$and"] = [{"$or": s["$or"]}]

    if query:
        if not query.get("$match"):
            return {"$match": query}
        return query

    return None


def paginate(model, pagination, schema, search: dict = {}, aggregation: list = None, verbose: bool =False) -> dict:
    per_page: int = pagination.per_page
    page: int = pagination.page
    sort_field, order = pagination.sort.split("|")

    order_dir: dict = {
        "ascending": 1,
        "descending": -1,
        "desc": -1,
        "asc": 1
    }

    query: Union[None, dict] = construct_search(schema, pagination.search, search)
    aggs: list = []

    if query:
        aggs.append(query)

    agg_sort: dict = {
        "$sort": {
            sort_field: order_dir.get(order, -1)
        }
    }

    skip: int = (page-1)*per_page

    agg_skip: dict = {
        "$skip": skip,
    }

    agg_limit: dict = {
        "$limit": per_page
    }

    aggs.extend([agg_sort, agg_skip, agg_limit])

    if aggregation:
        aggs.extend(aggregation)

    aggs.append(agg_sort)
    logger.debug(f"Executing aggregation {aggs} on model {str(model)}")
 
    objects: list = model.objects.aggregate(*aggs)

    count_query: dict = { 
        "$group": { "_id": None, "count": { "$sum": 1 } } 
    }

    if query:
        try:
            aggs_count: list = [query, count_query]
            total_objects: int = list(model.objects.aggregate(*aggs_count))[0]["count"]
        except IndexError:
            total_objects: int = 0
    else:
        total_objects: int = model.objects.count()

    data: list = []
    for doc in objects:
        data.append(jsonable_encoder(schema(**doc)))

    return {
        "data": data,
        "from": skip,
        "current_page": page,
        "per_page": per_page,
        "to": skip + len(data),
        "total": total_objects,
        "last_page": math.ceil(total_objects / per_page)
    }
