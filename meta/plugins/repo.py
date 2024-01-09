from cutekit import cli, model, shell, const
from . import utils

import os
import subprocess

@cli.command("r", "odoo/repo", "Manage Odoo repository.")
def _(args: cli.Args):
    ...

@cli.command("S", "odoo/repo/switch", "Switch Odoo repository branch.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    cache["ODOO_VERSION"] = args.consumeOpt("ver", "master")
    utils.branchSwitch(cache["ODOO_VERSION"], cache)
    cache.finilize()


@cli.command("s", "odoo/repo/search", "Search branch in Odoo repository.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    branches = []
    for repo in cache.registry.project.externDirs:
        branches += list(filter(lambda b: bool(b), shell.popen("git", "-C", cache.rootdir / repo, "branch", "-r").split()))

    branches = list(set(branches))
    branch = subprocess.run(["fzf", "--ansi", "-1"], input="\n".join(branches), text=True, stdout=subprocess.PIPE).stdout.split("/")[1].strip()
    cache["ODOO_VERSION"] = branch
    utils.branchSwitch(branch, cache)
    cache.finilize()


@cli.command("r", "odoo/repo/rebase", "Rebase Odoo repository.")
def _(args: cli.Args):
    target = args.consumeOpt("target", "master")
    cache = utils.Cache(model.Registry.use(args))

    for repo in cache.registry.project.externDirs:
        shell.exec("git", "-C", cache.rootdir / repo, "fetch", "origin", target)
        shell.exec("git", "-C", cache.rootdir / repo, "rebase", f"origin/{target}")


@cli.command("f", "odoo/repo/force", "Force push Odoo repository.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    for repo in cache.registry.project.externDirs:
        branch = shell.popen("git", "-C", cache.rootdir / repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}").strip().split("/")

        if branch[0] != "dev" and repo:
            if branch[1] == "master" or repo != os.path.join(const.EXTERN_DIR, "odoo", "upgrade"):
                print("[-] Branch is not dev")
                continue

        try:
            shell.exec("git", "-C", cache.rootdir / repo, "diff", "--quiet", "HEAD")
            shell.exec("git", "-C", cache.rootdir / repo, "commit", "--amend", "--no-edit")
        except RuntimeError:
            print("No changes in branch")
            pass

        shell.exec("git", "-C", cache.rootdir / repo, "push", "--force")


@cli.command("R", "odoo/repo/refresh", "Refresh Odoo repository.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    for repo in cache.registry.project.externDirs:
        remotes = shell.popen("git", "-C", cache.rootdir / repo, "remote").split()
        for remote in remotes:
            shell.exec("git", "-C", cache.rootdir / repo, "fetch", remote)


@cli.command("m", "odoo/repo/master", "Switch Odoo repository to master.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    cache["ODOO_VERSION"] = "master"
    utils.branchSwitch("master", cache)
    cache.finilize()


@cli.command("c", "odoo/repo/clean", "Clean Odoo repository.")
def _(args: cli.Args):
    cache = utils.Cache(model.Registry.use(args))
    for repo in cache.registry.project.externDirs:
        shell.exec("git", "-C", cache.rootdir / repo, "stash")