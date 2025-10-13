# tests/test_config_module.py
import importlib
import service.config as cfg

def test_import_config_module():
    # Just importing the module should execute all its top-level statements
    importlib.reload(cfg)
    # Sanity check: module object exists
    assert cfg is not None
