from cutekit import cli, model, shell, const
from pathlib import Path
from tempfile import NamedTemporaryFile
import os
import sys
from . import utils


@cli.command("T", "odoo/script", "Run a script")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    cache["SCRIPT"] = args.consumeArg(cache.get("SCRIPT", None))
    cache["PERF"] = args.consumeOpt(cache.get("PERF", False))

    script = Path(cache["SCRIPT"])
    with (Path(__file__).absolute().parent / "prelude.py").open("r") as f:
        prelude = f.read().format(
            ODOO_PATH=str(
                cache.rootdir
                / const.EXTERN_DIR
                / "odoo"
                / "odoo"
                / "odoo"
                / "__init__.py"
            ),
            UPGRADE_PATH = str(
                cache.rootdir
                / const.EXTERN_DIR
                / "odoo"
                / "upgrade-util"
                / "src"
                / "util"
                / "__init__.py"
            )
        )

    with script.open("r") as f:
        script_content = f"{prelude}\n{f.read()}"

    utils.ensureVenv(cache)

    # Python binary
    python = Path(sys.executable)

    with NamedTemporaryFile(suffix=".py", mode="w") as f:
        f.write(script_content)
        f.flush()

        if cache["PERF"]:
            try:
                shell.exec(
                    "py-spy",
                    "record",
                    "--format",
                    "speedscope",
                    "--output",
                    "profile.speedscope.json",
                    "-r",
                    "1000",
                    "--",
                    str(python),
                    str(f.file.name),
                )
            except RuntimeError:
                pass
        else:
            shell.exec(python, f.file.name)

    if cache["PERF"]:
        shell.exec("speedscope", "profile.speedscope.json")
        shell.rmrf("profile.speedscope.json")
