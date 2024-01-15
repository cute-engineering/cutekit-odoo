from cutekit import cli

@cli.command("o", "odoo", "Open Source Apps To Grow Your Business.")
def _(args: cli.Args):
    ...

from . import (
    venv,
    repo,
    instance,
    misc
)

try:
    from . import private
except ImportError:
    pass
