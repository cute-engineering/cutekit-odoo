from os import environ
from cutekit import cli, model, shell, const
from pathlib import Path

from . import utils

CK_PATH = Path.home() / "Developer" / "cutekit"

@cli.command("v", "odoo/venv", "Manage Odoo virtual environment.")
def _(args: cli.Args):
    ...

@cli.command("a", "odoo/venv/activate", "Activate Odoo virtual environment.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.10"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    shell.exec("fish", "-C", f"source \"$PYENV_ROOT/versions/odoo-{cache['ODOO_VERSION']}/bin/activate.fish\"")

    cache.finilize()

@cli.command("i", "odoo/venv/init", "Initialize Odoo virtual environment.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    pip_path = Path(environ["PYENV_ROOT"]) / "versions" / f"odoo-{cache['ODOO_VERSION']}" / "bin" / "pip"

    shell.exec("pyenv", "install", "-s", cache["PYTHON_VERSION"])
    shell.exec("pyenv", "virtualenv", "-f", cache["PYTHON_VERSION"], f"odoo-{cache['ODOO_VERSION']}")

    utils.branchSwitch(cache["ODOO_VERSION"], cache)

    shell.exec(pip_path, "install", "-r", cache.rootdir / const.EXTERN_DIR / "odoo" / "odoo"/ "requirements.txt")
    shell.exec(pip_path, "install", ".", cwd=CK_PATH)

    cache.finilize()