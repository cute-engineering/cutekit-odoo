from cutekit import cli, model, shell
from tempfile import gettempdir
from pathlib import Path
from . import utils

import os
import json


@cli.command("e", "odoo/edit", "Edit Odoo source code.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    utils.ensureVenv(cache)

    cfg = {
        "folders": [{ 'path': str(Path(e).absolute()) } for e in cache.registry.project.externDirs],
        "settings": {
            "python.defaultInterpreterPath": str(Path(os.environ['PYENV_ROOT']) / "versions" / f"odoo-{cache['ODOO_VERSION']}")
        }
    }

    with open(Path(gettempdir()) / "odoo.code-workspace", "w") as f:
        json.dump(cfg, f)
        shell.exec("code", f.name)

    cache.finilize()
