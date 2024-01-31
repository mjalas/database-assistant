from database_assistant.dynamodb.commands import (
    import_csv,
    list_tables,
    get_data,
    get_local_data,
    delete_table,
    import_from_cloud_to_local,
)
from database_assistant.utils import typerInstance

local = typerInstance()
local.command()(delete_table)
local.command()(list_tables)
local.command(name="get-data")(get_local_data)
local.command()(import_csv)


app = typerInstance()
app.add_typer(local, name="local")
app.command()(get_data)
app.command()(import_from_cloud_to_local)

if __name__ == "__main__":
    app()
