from .witty import WITTY
from tempfile import TemporaryDirectory

import logging
import random
import uuid
import os.path

srcDirectory = TemporaryDirectory()

def httpTestNoTimeout():
    from odoo.tests.common import BaseCase
    from requests import PreparedRequest, Session

    _request_handler_orig = BaseCase._request_handler
    def _request_handler(s: Session, r: PreparedRequest, /, **kw):
        kw["timeout"] = None
        _request_handler_orig(s, r, **kw)
    BaseCase._request_handler = _request_handler

def odooTestWitty():
    from odoo.tests.result import OdooTestResult

    def logError(self, flavour, test, error):
        err = self._exc_info_to_string(error, test)
        caller_infos = self.getErrorCallerInfo(error, test)
        self.log(logging.INFO, '=' * 70, test=test, caller_infos=caller_infos)  # keep this as info !!!!!!
        self.log(logging.ERROR, "%s: \033[36m%s\033[0m\n%s", flavour, random.choice(WITTY), err, test=test, caller_infos=caller_infos)

    OdooTestResult.logError = logError


def compileKeepSrc():
    compile_orig = __builtins__["compile"]
    def new_compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, *, _feature_version=-1):
        if isinstance(source, str):
            filename = os.path.join(srcDirectory.name, uuid.uuid4().hex)
            with open(filename, "w") as f:
                f.write(source)
                f.flush()

        return compile_orig(source, filename, mode, flags, dont_inherit, optimize, _feature_version=_feature_version)

    __builtins__["compile"] = new_compile