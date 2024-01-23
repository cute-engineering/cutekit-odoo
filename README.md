<br/>
<br/>
<br/>
<p align="center">
    <img src="doc/logo.svg" width="200" height="200">
</p>
<h1 align="center">Odoo + Cutekit = :heart:</h1>
<p align="center">
    <b>Odoo</b> with the power of Cutekit, the *magical* build system and package manager
</p>
<br/>
<br/>
<br/>

> [!warning]
> this project uses the unstable [cutekit 0.7](https://github.com/cute-engineering/cutekit/tree/0.7-dev)

## Available commands
### Branch management
1. Switch
```shell
$ cutekit odoo repo switch --ver=branch
$ ck o r s --ver=branch
```
This will switch every repositories mentionned in [project.json](./project.json) to the specified branch

2. Search
```shell
$ cutekit odoo repo search
$ ck o r S
```
This will bring up a menu and you can choose a branch, it will switch every repositories mentionned in [project.json](./project.json)

2. Rebase
```shell
$ cutekit odoo repo rebase (--target=master) (--select)
$ ck o r r (--target=master) (--select)
```
Will rebase every repositories mentionned in [project.json](./project.json) to the branch mentionned by the `target` parameter. If not provided, the default target is the `master` branch.
By default, it will rebase every repository. Use the `--select` switch to select which directories you want to rebase.

3. Force push
```shell
$ cutekit odoo repo force
$ ck o r f
```
This command will monitor changes (due to code modification or rebase) on branches present on your defined `dev` remote. It will leave `origin` remotes untouched

4. Back to master
```shell
$ cutekit odoo repo master
$ cutekit o r m
```
Will go back to master on every repositories mentionned in [project.json](./project.json)

5. Clean
```shell
$ cutekit odoo repo clean
$ cutekit o r c
```

Will stash every changes

### Virtualenv management
> [!warning]
> Those options requires [pyenv](https://github.com/pyenv/pyenv)

1. Activate (:warning: fish only)
```shell
$ cutekit odoo venv activate (--py-ver=3.11) (--ver=master)
$ ck o v a (--py-ver=3.11) (--ver=master)
```
Will give you shell access to the venv used to run a specified Odoo instance

2. Init
```shell
$ cutekit odoo venv init (--py-ver=3.11) (--ver=master)
$ ck o v i (--py-ver=3.11) (--ver=master)
```
Will create automaticly a Python virtualenv with every dependencies installed

### Instance management

All of those options are using some sort of cache to remember your last choices!

1. Init
```shell
$ cutekit odoo init (--py-ver=3.11) (--ver=master)
$ ck o i
```
Create a new Odoo instance. A addons menu will popup and will asks you which modules you want to install.

2. Start
```shell
$ cutekit odoo start (--py-ver=3.11) (--ver=master)
$ ck o s (--py-ver=3.11) (--ver=master)
```
Will start a previously initialised Odoo instance

3. Test
```shell
$ cutekit odoo test (--pyver=3.11) (--ver=master) TEST_TAGS
$ ck o t (--pyver=3.11) (--ver=master) TEST_TAGS
```
Will run a test. Please read [Odoo's documentation about test](https://www.odoo.com/documentation/17.0/developer/reference/backend/testing.html) for more informations.

4. Shell
```shell
$ cutekit odoo shell (--pyver=3.11) (--ver=master)
$ ck o S (--pyver=3.11) (--ver=master)
```
Will run the Odoo shell with the default Python interpreter.

### Misc

1. Edit
```shell
$ cutekit odoo edit (--pyver=3.11) (--ver=master) (--no-ext)
$ ck o e (--pyver=3.11) (--ver=master) (--no-ext)
```

This command will create a vscode workspace and will also configure the Odoo extension. use the `no-ext` if you didn't install the official Odoo extension.

2. Goto
```shell
$ cutekit odoo goto
$ ck o g
```
Simple command that will change your CWD to the repository you select.

## Use it with Nix

You can use Nix to make an environment with all the necessary dependencies :

```bash
$ nix develop ./meta/nix
```

## License

<a href="https://opensource.org/licenses/MIT">
  <img align="right" height="96" alt="MIT License" src="https://raw.githubusercontent.com/skift-org/skift/main/doc/mit.svg" />
</a>

The Odoo cutekit and its core components are licensed under the **MIT License**.

The full text of the license can be accessed via [this link](https://opensource.org/licenses/MIT) and is also included in the [LICENSE](LICENSE) file of this software package.
