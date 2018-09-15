import os
from pytest import raises, mark, fixture
from voidpp_tools.mocks.file_system import mockfs

from configpp.evolution import Evolution, EvolutionException
from configpp.evolution.revision import Revision

from .utils import FileSystem, mock_import


def test_init():
    fs_data = {}

    fs = FileSystem(fs_data)

    with fs.mock():
        ev = Evolution()

        assert ev.init('evolution')
        assert 'evolution' in fs_data
        assert 'evolution.yaml' in fs_data
        assert 'versions' in fs_data['evolution']

@mockfs({'evolution': {'versions':{}}, 'evolution.yaml': 'script_location: evolution'})
def test_load():

    ev = Evolution()
    assert ev.load()


@mockfs({'evolution': {'versions':{}}, 'evolution.yaml': 'script_location: evolution42'})
def test_load_nonexists_folder():

    ev = Evolution()
    assert ev.load() is False
