import typer

from database_assistant.dynamodb.commands import import_csv

app = typer.Typer()
app.command()(import_csv)


if __name__ == "__main__":
    app()
