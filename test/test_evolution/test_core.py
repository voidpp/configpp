import os
import yaml
from voidpp_tools.mocks.file_system import mockfs
from configpp.evolution import Evolution, Revision

from .utils import FileSystem

def test_init():
    template_file_path = Revision.ORIGINAL_TEMPLATE_FILE_PATH
    with open(template_file_path) as f:
        template_file_content = f.read()

    fs_data = {}

    fs = FileSystem(fs_data)
    fs.set_data(Revision.ORIGINAL_TEMPLATE_FILE_PATH, template_file_content, True)

    with fs.mock():
        ev = Evolution()

        assert ev.init('evolution')
        assert 'evolution' in fs_data
        assert 'evolution.yaml' in fs_data
        assert 'versions' in fs_data['evolution']
        config = yaml.load(fs_data['evolution.yaml'], Loader = yaml.FullLoader)
        assert 'revision_template_file' in config
        assert config['revision_template_file']
        assert fs.get_data(config['revision_template_file'])


@mockfs({'evolution': {'versions':{}}, 'evolution.yaml': 'script_location: evolution\nrevision_template_file: some\nconfigpp_urls: {}'})
def test_load():

    ev = Evolution()
    assert ev.load()


@mockfs({'evolution': {'versions':{}}, 'evolution.yaml': 'script_location: evolution42\nrevision_template_file: some\nconfigpp_urls: {}'})
def test_load_nonexists_folder():

    ev = Evolution()
    assert ev.load() is False
