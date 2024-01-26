{
  description = "Nix + Cutekit + Odoo = <3";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.11";
    cutekit.url = "github:cute-engineering/cutekit/0.7-dev?dir=meta/nix";
  };

  outputs = { self, nixpkgs, cutekit, ... }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      ck = cutekit.defaultPackage.x86_64-linux;
      cwd = builtins.toString ./.;

      wmctrl = pkgs.python311Packages.buildPythonPackage {
        name = "wmctrl";
        version = "0.5";
        pyproject = true;

        nativeBuildInputs = with pkgs.python311Packages; [ setuptools ];

        src = pkgs.python311Packages.fetchPypi {
          pname = "wmctrl";
          version = "0.5";
          sha256 = "sha256-eDmja2/p4tb9IjBOXcNy287SEWukEoPqk4stpX9T6WI=";
        };
      };

      pyrepl = pkgs.python311Packages.buildPythonPackage {
        name = "pyrepl";
        version = "master";

        buildInputs = [ pkgs.ncurses ];

        nativeBuildInputs = with pkgs.python311Packages; [ setupmeta ];
        propagatedBuildInputs = with pkgs.python311Packages; [ pkgs.ncurses pytest pexpect pygame ];

        src = builtins.fetchGit {
          url = "https://github.com/pypy/pyrepl";
          rev = "ca192a80b76700118b9bfd261a3d098b92ccfc31";
        };

        prePatch = ''
          export LD_LIBRARY_PATH=${
            pkgs.lib.makeLibraryPath [ pkgs.ncurses ]
          }
        '';

        patches = [ ./001-pyrepl-neq.diff ];
      };

      fancycompleter = pkgs.python311Packages.buildPythonPackage {
        name = "fancycompleter";
        version = "0.8";

        nativeBuildInputs = with pkgs.python311Packages; [ setupmeta ];
        propagatedBuildInputs = [ pyrepl ];

        src = builtins.fetchGit {
          url = "https://github.com/pdbpp/fancycompleter";
          rev = "67e3ec128cf8d44be6e48e775234c07f4b23064e";
        };
      };

      pdbpp = pkgs.python311Packages.buildPythonPackage {
        pname = "pdbpp";
        version = "0.10.3";
        nativeBuildInputs = with pkgs.python311Packages; [
          setuptools_scm
          pkgs.ncurses
        ];
        propagatedBuildInputs = with pkgs.python311Packages; [
          pygments
          wmctrl
          fancycompleter
          six
          pkgs.ncurses
        ];

        src = pkgs.fetchFromGitHub {
          owner = "pdbpp";
          repo = "pdbpp";
          rev = "e1c2e347cc55a6dd89e058e56a1366ada68884bc";
          sha256 = "sha256-PDYt90cguOvxXk0gocZWnPv7fsNm2/wPrZ8lxRsNFMM=";
        };

        patches = [ ./002-pdbpp-setup.diff ];

      };

    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = with pkgs; [
          ck
          fzf
          pdbpp

          # Odoo's dependencies
          postgresql
          python311Packages.babel
          python311Packages.chardet
          python311Packages.cryptography
          python311Packages.decorator
          python311Packages.docutils
          python311Packages.ebaysdk
          python311Packages.freezegun
          python311Packages.gevent
          python311Packages.greenlet
          python311Packages.idna
          python311Packages.jinja2
          python311Packages.libsass
          python311Packages.lxml
          python311Packages.markupsafe
          python311Packages.num2words
          python311Packages.ofxparse
          python311Packages.passlib
          python311Packages.pillow
          python311Packages.polib
          python311Packages.psutil
          python311Packages.psycopg2
          python311Packages.pydot
          python311Packages.pyopenssl
          python311Packages.pypdf2
          python311Packages.pyserial
          python311Packages.python-dateutil
          python311Packages.python-ldap
          python311Packages.python-stdnum
          python311Packages.pytz
          python311Packages.pyusb
          python311Packages.qrcode
          python311Packages.reportlab
          python311Packages.requests
          python311Packages.urllib3
          python311Packages.vobject
          python311Packages.werkzeug
          python311Packages.xlrd
          python311Packages.xlsxwriter
          python311Packages.xlwt
          python311Packages.zeep
          python311Packages.setuptools
          python311Packages.mock
          python311Packages.rjsmin
          python311Packages.geoip2
        ];

        PGDATA = "/tmp/odoo-pgdata";

        shellHook = ''
          echo "Using ${pkgs.postgresql.name}."

          # Setup: other env variables
          export PGHOST="$PGDATA"
          # Setup: DB
          [ ! -d $PGDATA ] && pg_ctl initdb -o "-U $(whoami)"
          pg_ctl -o "-p 5432 -k $PGDATA" start
          alias fin="pg_ctl stop && exit"
          alias pg="psql -p 5432 -U postgres"

          # Uncomment if you want to use fish
          fish
          fin
          exit

          # Comment if you want to use fish (it doesn't work with fish for some reason)
          # trap fin EXIT
        '';
      };
    };
}
