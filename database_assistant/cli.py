import typer

from database_assistant.dynamodb.commands import (
    import_csv,
    list_tables,
    get_data,
    delete_table,
    import_from_cloud_to_local,
)

app = typer.Typer()
app.command()(import_csv)
app.command()(list_tables)
app.command()(get_data)
app.command()(delete_table)
app.command()(import_from_cloud_to_local)


def main():
    app()
