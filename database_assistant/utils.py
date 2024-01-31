import typer


def typerInstance():
    return typer.Typer(no_args_is_help=True)
