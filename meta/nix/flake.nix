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

    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = with pkgs; [
          ck
          fzf

          # Odoo's dependencies
          postgresql
          killall
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
          # fish
          # fin
          # exit

          # Comment if you want to use fish (it doesn't work with fish for some reason)
          trap fin EXIT
        '';
      };
    };
}
