from cutekit import cli, model, shell
from pathlib import Path
import subprocess

from . import utils
from . import monkeys
from . import unwrapper

@cli.command("i", "odoo/init", "Create a new Odoo instance.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    utils.ensureVenv(cache)
    utils.bootstrapOdoo(cache)

    new = args.consumeOpt("new", False)
    stop = args.consumeOpt("stop", False)
    
    from odoo.tools.config import config
    from odoo.modules.module import get_modules, initialize_sys_path
    from odoo.service.db import _create_empty_database, DatabaseExists

    config.parse_config()
    config["addons_path"] = "," + ",".join([str(Path(e).absolute()) for e in cache.registry.project.externDirs])
    initialize_sys_path()

    if new or not cache.get("MODULES"):
        cache["MODULES"] = subprocess.run(["fzf", "--ansi", "-m"], input="\n".join(get_modules()), text=True, stdout=subprocess.PIPE).stdout.split()

    config["init"] = {k: True for k in cache["MODULES"] + ["base"]}
    config["db_name"] = f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
    config["db_host"] = "127.0.0.1"
    config["http_interface"] = "127.0.0.1"
    config['stop_after_init'] = stop

    try:
        shell.exec("dropdb", config['db_name'])
    except RuntimeError:
        pass

    _create_empty_database(config["db_name"])

    cache.finilize()
    utils.startOdoo(stop=stop)


@cli.command("s", "odoo/start", "Start an Odoo instance.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    utils.ensureVenv(cache)
    utils.bootstrapOdoo(cache)

    from odoo.tools.config import config

    config.parse_config()
    config["addons_path"] = utils.getOdooAddonsPath(cache)
    config["db_name"] = f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
    config["db_host"] = "127.0.0.1"
    config["http_interface"] = "127.0.0.1"

    cache.finilize()
    utils.startOdoo()


@cli.command("S", "odoo/shell", "Run Odoo shell.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    utils.ensureVenv(cache)
    utils.bootstrapOdoo(cache)

    from odoo.tools.config import config
    from odoo.cli.command import commands

    config.parse_config()
    config["addons_path"] = utils.getOdooAddonsPath(cache)
    config["db_name"] = f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
    config["db_host"] = "127.0.0.1"
    config["http_interface"] = "127.0.0.1"
    config["shell_interface"] = "python"

    cache.finilize()

    commands["shell"]().run(None)


@cli.command("t", "odoo/test", "Run Odoo tests.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["TEST_TAGS"] = args.consumeArg() or cache["TEST_TAGS"]
    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    utils.ensureVenv(cache)
    utils.bootstrapOdoo(cache)

    from odoo.tools.config import config

    monkeys.odooTestWitty()
    monkeys.compileKeepSrc()
    monkeys.customDebuggerFunc()

    config.parse_config()
    config["test_enable"] = True
    config["test_tags"] = cache["TEST_TAGS"]
    config["addons_path"] = utils.getOdooAddonsPath(cache)
    config["db_name"] = f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
    config["db_host"] = "127.0.0.1"
    config["http_interface"] = "127.0.0.1"

    cache.finilize()
    # unwrapper.addSafeEvalUnwrapBuiltins()
    utils.startOdoo(stop=True)