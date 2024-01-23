from cutekit import model, const, shell
from pathlib import Path
from typing import Optional
from collections import UserDict
import importlib.util as importlib

import os
import json
import sys

class Cache(UserDict):
    def __init__(self, registry: model.Registry, path: Optional[Path] = None):
        self.rootdir = Path(registry.project.path).parent
        self.path = path or self.rootdir / const.CACHE_DIR / ".cache"
        self.path.parent.mkdir(exist_ok=True, parents=True)
        self.registry = registry

        if self.path.exists():
            with self.path.open("r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item):
        return self.data[item]

    def finilize(self):
        with self.path.open("w") as f:
            json.dump(self.data, f)


def branchSwitch(branch_name: str, cache: Cache):
    for repo in cache.registry.project.externDirs:
        try:
            shell.exec("git", "-C", cache.rootdir / repo, "checkout", "--quiet", branch_name)
        except RuntimeError:
            print(f"[-] Branch {branch_name} not found in {repo}")
            shell.exec("git", "-C", cache.rootdir / repo, "checkout", "--quiet", "master")

def ensureVenv(cache: Cache):
    if "IN_NIX_SHELL" in os.environ:
        return # Thy shall not use virtual environments in nix-shell

    if not str(Path(sys.executable).parent).startswith(str(Path(os.environ["PYENV_ROOT"]))):
        env_path = Path(os.environ["PYENV_ROOT"]) / "versions" / f"odoo-{cache['ODOO_VERSION']}"

        if not env_path.exists():
            env_path = Path(os.environ["PYENV_ROOT"]) / "versions" / f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
            if not env_path.exists():
                print("[-] Virtual environment not found")
                return

        shell.exec(env_path / "bin" / "python", "-m", "cutekit", *sys.argv[1:], cwd=cache.rootdir)
        exit()

def bootstrapOdoo(cache: Cache):
    odoo_path = cache.rootdir / const.EXTERN_DIR / "odoo" / "odoo" / "odoo" / "__init__.py"
    spec = importlib.spec_from_file_location("odoo", odoo_path)
    module = importlib.module_from_spec(spec)
    sys.modules["odoo"] = module
    spec.loader.exec_module(module)

def startOdoo(stop: bool = False):
    from odoo.tools.config import config
    from odoo.service.server import start
    from odoo.netsvc import init_logger

    init_logger()

    exit(
        start(
            preload=config["db_name"].split(","),
            stop=stop
        )
    )

def getOdooAddonsPath(cache: Cache) -> str:
    addons_path = ""

    for repo in cache.registry.project.externDirs:
        if repo.endswith("odoo"):
            addons_path += str(Path(cache.rootdir / repo / "addons").absolute())
        else:
            addons_path += str(Path(cache.rootdir / repo).absolute())
        addons_path += ","

    return addons_path[:-1]