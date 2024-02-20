from cutekit import cli, const, model, shell
from tempfile import gettempdir
from pathlib import Path
from . import utils

import sys
import subprocess
import os
import json
import sqlite3


@cli.command("c", "odoo/cache", "Dump the cache")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    for key, value in cache.items():
        print(f"{key} = {value}")


@cli.command("g", "odoo/goto", "Go to Odoo source code.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    directory = subprocess.run(
        ["fzf", "--ansi", "-1"],
        input="\n".join([Path(d).name for d in cache.registry.project.externDirs]),
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

    os.chdir(cache.rootdir / const.EXTERN_DIR / 'odoo' / directory)
    os.system("$SHELL")

@cli.command("e", "odoo/edit", "Edit Odoo source code.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))
    cache["NO_EXT"] = args.consumeOpt("no-ext", cache.get("NO_EXT", False))

    utils.ensureVenv(cache)


    env_path = Path(os.environ['PYENV_ROOT']) / "versions" / f"odoo-{cache['ODOO_VERSION']}"
    if not env_path.exists():
        env_path = Path(os.environ["PYENV_ROOT"]) / "versions" / f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
        if not env_path.exists():
            print("[-] Virtual environment not found")
            return

    cfg = {
        "folders": [{ 'path': str(Path(e).absolute()) } for e in cache.registry.project.externDirs],
        "settings": {
            "python.defaultInterpreterPath": str(env_path / "bin" / "python"),
            "python.analysis.extraPaths": [str(Path(e).absolute()) for e in cache.registry.project.externDirs],
        }
    }

    if not cache["NO_EXT"]:
        con = sqlite3.connect(Path.home() / ".config" / "Code" / "User" / "globalStorage" / "state.vscdb")
        cur = con.cursor()

        res = cur.execute("SELECT value FROM ItemTable WHERE key = 'Odoo.odoo'")
        code_cfg = json.loads(res.fetchone()[0])

        code_cfg['Odoo.nextConfigId'] = 1
        code_cfg['Odoo.configurations'] = {
            '0': {
                'id': 0,
                'name': 'Odoo - auto-generated by cutekit',
                'odooPath': next(filter(lambda e: e['path'].endswith('odoo'), cfg["folders"]))['path'],
                'addons': [e['path'] for e in cfg["folders"] if not e['path'].endswith('odoo')],
                'pythonPath':  str(env_path / "bin" / "python"),
            }
        }

        cur.execute("UPDATE ItemTable SET value = ? WHERE key = 'Odoo.odoo'", (json.dumps(code_cfg),))
        con.commit()

    with open(Path(gettempdir()) / "odoo.code-workspace", "w") as f:
        json.dump(cfg, f)
        shell.exec("code", f.name)

    cache.finilize()
