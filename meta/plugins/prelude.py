import importlib.util as importlib
import sys

odoo_path = "{ODOO_PATH}"
spec = importlib.spec_from_file_location("odoo", odoo_path)
module = importlib.module_from_spec(spec)
sys.modules["odoo"] = module
spec.loader.exec_module(module)

upgrade_path = "{UPGRADE_PATH}"
spec = importlib.spec_from_file_location("upgrade_util", upgrade_path)
module = importlib.module_from_spec(spec)
sys.modules["upgrade_util"] = module
spec.loader.exec_module(module)

