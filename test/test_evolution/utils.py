
from importlib.machinery import SourceFileLoader
import importlib.util
from contextlib import contextmanager
from unittest.mock import patch
from configpp.soil import YamlTransform
from voidpp_tools.mocks.file_system import FileSystem as FileSystemBase

class MockSourceLoader(SourceFileLoader):
    """Source loader for the voidpp_tools based file system mock

    This is a really weird hack, but the importlib is poorly documented and there is no example in the net about it. Really. Nothing...
    """

    def __init__(self, fs: FileSystemBase, filename, name = 'dummy'):
        self._fs = fs
        self.name = name
        self.path = filename

    def get_data(self, path):
        return self._fs.get_data(path)

class FileSystem(FileSystemBase):
    """This is a generic tool to "import" from the fake file system

        Note: yeah, this is looks like generic, and it is. But there is no other place right now, because this is python3 only and the
        voidpp-tools has to work with python2.7 ...
    """

    def import_file(self, path):

        loader = MockSourceLoader(self, path)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)

        return mod

class SpiderManTransform(YamlTransform):
    pass

@contextmanager
def mock_import(fs):
    with patch('configpp.evolution.chain.import_file', new = fs.import_file):
        yield
