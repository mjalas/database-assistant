from typing import Annotated
import boto3
import json
from rich import print
from rich.progress import track

import typer
from database_assistant.csv_parsers import parse_csv
from database_assistant.dynamodb.models import create_pynamodb_model_from_data


def _get_db_client(host: str = None, region: str = None, profile: str = None):
    if profile:
        boto3.setup_default_session(profile_name=profile)
        client = boto3.client("dynamodb")
    elif host and region:
        client = boto3.client("dynamodb", endpoint_url=host, region_name=region)
    else:
        raise Exception("Either profile or host and region must be provided.")
    return client


def import_csv(
    csv_file: str,
    table_name: Annotated[
        str, typer.Argument(help="Name of the local DynamoDB table to import data to.")
    ],
    region: Annotated[str, typer.Argument(envvar="DB_REGION")],
    host: Annotated[str, typer.Argument(envvar="DB_HOST")] = "",
):
    """Import data to a local DynamoDB table from a CSV file."""
    data = parse_csv(filepath=csv_file)

    DBModel = create_pynamodb_model_from_data(
        obj=data[0], table_name=table_name, host=host, region=region
    )
    if not DBModel.exists():
        DBModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    for row in data:
        item = DBModel(**row)
        item.save()
    print(f"Imported {DBModel.count()} items")


def list_tables(
    host: Annotated[
        str,
        typer.Argument(
            envvar="DB_HOST", help="Host URL, e.g. when connecting to local database."
        ),
    ],
    region: Annotated[str, typer.Argument(envvar="DB_REGION")],
):
    """List local DynamoDB tables."""

    ddb = boto3.client("dynamodb", endpoint_url=host, region_name=region)
    response = ddb.list_tables()
    if "TableNames" in response:
        print(response["TableNames"])
    else:
        print("Could not find any tables")


def get_data(
    table_name: Annotated[
        str, typer.Argument(help="Name of the DynamoDB table to get data from.")
    ],
    to_file: Annotated[
        str, typer.Option(help="File path where to store the result.")
    ] = None,
    host: Annotated[
        str,
        typer.Option(
            envvar="DB_HOST", help="Host URL, e.g. when connecting to local database."
        ),
    ] = None,
    region: Annotated[
        str,
        typer.Option(
            envvar="DB_REGION",
            help="AWS REGION, use e.g. when connecting to local database",
        ),
    ] = None,
    profile: Annotated[
        str,
        typer.Option(
            envvar="AWS_PROFILE", help="SSO profile for connecting to AWS DynamoDB"
        ),
    ] = None,
):
    """Fetch data from either a local or cloud DynamoDB table."""
    ddb = _get_db_client(host=host, region=region, profile=profile)
    data = ddb.scan(TableName=table_name)
    if to_file:
        with open(to_file, "w") as dest:
            json.dump(data, dest, indent=4, sort_keys=False)
    else:
        print(data)


def import_from_cloud_to_local(
    table_name: Annotated[
        str, typer.Argument(help="Name of the DynamoDB table to get data from.")
    ],
    local_host: Annotated[
        str,
        typer.Option(
            envvar="DB_HOST", help="Host URL, e.g. when connecting to local database."
        ),
    ] = None,
    region: Annotated[
        str,
        typer.Option(
            envvar="DB_REGION",
            help="AWS REGION, use e.g. when connecting to local database",
        ),
    ] = None,
    profile: Annotated[
        str,
        typer.Option(
            envvar="AWS_PROFILE", help="SSO profile for connecting to AWS DynamoDB"
        ),
    ] = None,
):
    """Import data from DynamoDB table in the cloud to a local instance."""

    print("Creating clients...", end="")
    local_client = boto3.client("dynamodb", endpoint_url=local_host, region_name=region)
    boto3.setup_default_session(profile_name=profile)
    cloud_client = boto3.client("dynamodb")
    print(" Done")
    print("Checking if local table exists...", end="")
    response = local_client.list_tables()
    if table_name not in response["TableNames"]:
        print(" No existing table")
        print("Creating new table...", end="")
        table_description = cloud_client.describe_table(TableName=table_name)["Table"]
        provisioned_throughput = table_description["ProvisionedThroughput"]
        if "NumberOfDecreasesToday" in provisioned_throughput:
            provisioned_throughput.pop("NumberOfDecreasesToday")
        response = local_client.create_table(
            AttributeDefinitions=table_description["AttributeDefinitions"],
            TableName=table_description["TableName"],
            KeySchema=table_description["KeySchema"],
            ProvisionedThroughput=provisioned_throughput,
        )
        print(" Done")
    else:
        print(" Existed, using existing table")

    print("Fetching data from cloud table...", end="")
    data_items = cloud_client.scan(TableName=table_name)["Items"]
    print(" Done")

    total_item_count = len(data_items)
    print(f"Items fetched {total_item_count}")
    for i in track(
        range(total_item_count), description="Importing data to local table..."
    ):
        local_client.put_item(TableName=table_name, Item=data_items[i])
    print(" Done")


def delete_table(
    table_name: Annotated[
        str, typer.Argument(help="Name of the local DynamoDB table to delete.")
    ],
    host: Annotated[str, typer.Argument(envvar="DB_HOST")],
    region: Annotated[str, typer.Argument(envvar="DB_REGION")],
):
    """Delete local table"""
    ddb = boto3.client("dynamodb", endpoint_url=host, region_name=region)
    res = ddb.delete_table(TableName=table_name)
    print(res)
