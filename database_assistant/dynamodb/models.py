from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    UTCDateTimeAttribute,
    BooleanAttribute,
    NumberAttribute,
    ListAttribute,
    MapAttribute,
)
from datetime import datetime


attribute_type_conversion = {
    str: UnicodeAttribute,
    datetime: UTCDateTimeAttribute,
    bool: BooleanAttribute,
    int: NumberAttribute,
    float: NumberAttribute,
    list: ListAttribute,
    dict: MapAttribute,
}


def create_pynamodb_model_from_data(obj: dict, table_name: str, host: str, region: str):
    base_object = obj

    def make_attributes(obj: dict) -> dict:
        attributes = {}

        for key, value in obj.items():
            if key == "id":
                attr_type = attribute_type_conversion[type(value)]
                attributes[key] = attr_type(hash_key=True)
            elif type(value) == list:
                if len(value) > 0 and type(value[0]) == dict:
                    pass
                else:
                    attributes[key] = attribute_type_conversion[type(value)]()
            elif type(value) == dict:
                attributes[key] = make_nested_attr(value)
            else:
                attributes[key] = attribute_type_conversion[type(value)]()

        return attributes

    def make_nested_attr(nested_schema):
        attributes = make_attributes(nested_schema)

        return type(nested_schema.__class__.__name__, (MapAttribute,), attributes)

    attributes = make_attributes(base_object)

    meta_attributes = {"table_name": table_name, "region": region, "host": host}
    attributes["Meta"] = type("Meta", (), meta_attributes)

    return type("DynamicModel", (Model,), attributes)
