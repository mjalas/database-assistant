import typer

from database_assistant.dynamodb import app as dynamodb_app

app = typer.Typer()
app.add_typer(dynamodb_app, name="dynamodb")


def main():
    app()
