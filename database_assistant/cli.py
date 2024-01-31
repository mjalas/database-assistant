import typer

from database_assistant.dynamodb import app as dynamodb_app
from database_assistant.utils import typerInstance

app = typerInstance()
app.add_typer(dynamodb_app, name="dynamodb")


def main():
    app()
