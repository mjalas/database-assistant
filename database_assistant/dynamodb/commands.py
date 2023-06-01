from typing import Annotated

import typer
from database_assistant.csv_parsers import parse_csv
from database_assistant.dynamodb.models import create_model_from_data


def import_csv(
    csv_file: str,
    table_name: str,
    host: Annotated[str, typer.Argument(envvar="DB_HOST")],
    region: Annotated[str, typer.Argument(envvar="DB_REGION")],
):
    data = parse_csv(filepath=csv_file)

    DBModel = create_model_from_data(
        obj=data[0], table_name=table_name, host=host, region=region
    )
    if not DBModel.exists():
        DBModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    for row in data:
        item = DBModel(**row)
        item.save()
    print(f"Imported {DBModel.count()} items")
