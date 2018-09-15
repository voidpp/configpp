
from logging import Logger
from importlib.machinery import SourceFileLoader
from functools import wraps
import importlib.util
from traceback import extract_stack

def import_file(path: str, name = 'dummy'):
    loader = SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod

def decorate_logger_message(format: str, logger_var_name = 'logger'):
    def decorator(func):
        globs = func.__globals__
        orig_logger = globs[logger_var_name] # type: Logger
        orig_logger_makeRecord = orig_logger.makeRecord

        def makeRecord(name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
            msg = format.format(original_message = msg)
            return orig_logger_makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)

        @wraps(func)
        def wrapper(*args, **kwargs):

            orig_logger.makeRecord = makeRecord

            try:
                res = func(*args, **kwargs)
            except:
                orig_logger.makeRecord = orig_logger_makeRecord
                raise

            orig_logger.makeRecord = orig_logger_makeRecord
            return res

        return wrapper
    return decorator

# TODO: context manager?
