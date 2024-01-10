from cutekit import cli, model, const
import subprocess
from . import utils

@cli.command("i", "odoo/init", "Create a new Odoo instance.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    utils.ensureVenv(cache)
    utils.bootstrapOdoo(cache)

    new = args.consumeOpt("n", False)
    stop = args.consumeOpt("s", False)
    
    from odoo.tools.config import config
    from odoo.modules.module import get_modules

    config["addons_path"] += "," + str(cache.rootdir / const.EXTERN_DIR / "odoo" / "enterprise")
    config.parse_config()

    if new:
        cache["MODULES"] = subprocess.run(["fzf", "--ansi", "-m"], input="\n".join(get_modules()), text=True, stdout=subprocess.PIPE).stdout.split()
    
    config["init"] = {k: 1 for k in cache["MODULES"]}
    config["db_name"] = f"odoo-{cache['ODOO_VERSION'].split('-')[0]})"
    config["db_host"] = "127.0.0.1"
    config["http_interface"] = "127.0.0.1"

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

    config["addons_path"] += "," + str(cache.rootdir / const.EXTERN_DIR / "odoo" / "enterprise")
    config["db_name"] = f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
    config["db_host"] = "127.0.0.1"
    config["http_interface"] = "127.0.0.1"

    cache.finilize()
    utils.startOdoo()

@cli.command("t", "odoo/test", "Run Odoo tests.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))

    cache["TEST_TAGS"] = args.consumeArg() or cache["TEST_TAGS"]
    cache["PYTHON_VERSION"] = args.consumeOpt("py-ver", cache.get("PYTHON_VERSION", "3.11"))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", cache.get("ODOO_VERSION", "master"))

    utils.ensureVenv(cache)
    utils.bootstrapOdoo(cache)

    from odoo.tools.config import config

    config["test_enable"] = True
    config["test_tags"] = cache["TEST_TAGS"]
    config["addons_path"] += "," + str(cache.rootdir / const.EXTERN_DIR / "odoo" / "enterprise")
    config["db_name"] = f"odoo-{cache['ODOO_VERSION'].split('-')[0]}"
    config["db_host"] = "127.0.0.1"
    config["http_interface"] = "127.0.0.1"

    cache.finilize()
    utils.startOdoo(stop=True)