import os
from pytest import raises, mark, fixture
from voidpp_tools.mocks.file_system import mockfs
from typing import Callable

from configpp.evolution import Evolution, EvolutionException
from configpp.evolution.revision import Revision
from configpp.soil import YamlTransform

from .utils import FileSystem, mock_import


@fixture()
def fs():

    template_file_path = Revision.ORIGINAL_TEMPLATE_FILE_PATH
    with open(template_file_path) as f:
        template_file_content = f.read()

    data = {
        'evolution': {
            'versions': {},
            'script.py.tmpl': template_file_content,
        },
        'etc': {},
    }

    fs = FileSystem(data)

    with fs.mock():
        with mock_import(fs):
            yield fs

@fixture()
def base_config():
    return {
        'script_location': 'evolution',
        'revision_template_file': 'evolution/script.py.tmpl',
        'configpp_urls': {},
    }

EVF = Callable[[], Evolution]

@fixture
def evf(base_config) -> EVF:
    """Evolution factory"""
    def factory():
        return Evolution(base_config)
    return factory


@fixture(scope = 'module')
def yaml():
    return YamlTransform()

def replace_content_in_rev_file(rev: Revision, fs: FileSystem, old: str, new: str):
    rev_file = 'evolution/versions/' + rev.filename
    data = fs.get_data(rev_file)
    fs.set_data(rev_file, data.replace(old, new))


def test_first_rev_single_config(fs: FileSystem, base_config):

    ev = Evolution(base_config)
    rev = ev.revision('test', 'configpp://app.json')
    replace_content_in_rev_file(rev, fs, "return config", "config.data = {'teve': 42}\n    return config")

    Evolution(base_config).upgrade()

    assert fs.get_data('/etc/app.json') == '{"teve": 42}'
    assert fs.get_data('/etc/app.json.version') == rev.id


def test_single_config_not_changed_upgrade_to_second_rev_from_empty(fs: FileSystem, base_config):

    ev = Evolution(base_config)
    rev1 = ev.revision('rev1', 'configpp://app.json')
    replace_content_in_rev_file(rev1, fs, "return config", "config.data = {'teve': 42}\n    return config")
    rev2 = ev.revision('rev2')
    replace_content_in_rev_file(rev2, fs, '"""put upgrade operations here"""', "config.data['teve'] *= 2")

    Evolution(base_config).upgrade()

    assert fs.get_data('/etc/app.json') == '{"teve": 84}'
    assert fs.get_data('/etc/app.json.version') == rev2.id


def test_single_config_not_changed_upgrade_to_second_rev_from_first_rev(fs: FileSystem, base_config):

    rev1 = Evolution(base_config).revision('rev1', 'configpp://app.json')
    replace_content_in_rev_file(rev1, fs, "return config", "config.data = {'teve': 42}\n    return config")
    Evolution(base_config).upgrade()
    assert fs.get_data('/etc/app.json') == '{"teve": 42}'

    rev2 = Evolution(base_config).revision('rev2')
    replace_content_in_rev_file(rev2, fs, '"""put upgrade operations here"""', "config.data['teve'] *= 2")

    Evolution(base_config).upgrade()

    assert fs.get_data('/etc/app.json') == '{"teve": 84}'
    assert fs.get_data('/etc/app.json.version') == rev2.id

def test_first_rev_group_config(fs: FileSystem, base_config):

    rev = Evolution(base_config).revision('test', 'configpp://core.json&logger.json@app1')
    replace_content_in_rev_file(rev, fs, "return config", "core.data = {'teve': 42}\n    logger.data = {'muha': 21}\n    return config")

    Evolution(base_config).upgrade()

    assert fs.get_data('/etc/app1/core.json') == '{"teve": 42}'
    assert fs.get_data('/etc/app1/.version') == rev.id

# TODO: test all config (grp member count/) changing scenarios

def test_group_config_add_new_member(fs: FileSystem, evf: EVF):

    rev1 = evf().revision('test1', 'configpp://core.json&logger.json@app1')
    replace_content_in_rev_file(rev1, fs, "return config", "core.data = {'teve': 42}\n    logger.data = {'muha': 21}\n    return config")

    evf().upgrade()

    rev2 = evf().revision('test2', 'configpp://core.json&logger.json&client.json@app1')
    replace_content_in_rev_file(rev2, fs, "{} # put initial data here", "{'id': 21}")

    evf().upgrade()

    assert fs.get_data('/etc/app1/core.json') == '{"teve": 42}'
    assert fs.get_data('/etc/app1/logger.json') == '{"muha": 21}'
    assert fs.get_data('/etc/app1/client.json') == '{"id": 21}'
    assert fs.get_data('/etc/app1/.version') == rev2.id

def test_group_config_remove_a_member(fs: FileSystem, evf: EVF):

    rev1 = evf().revision('test1', 'configpp://core.json&logger.json&client.json@app1')
    replace_content_in_rev_file(rev1, fs, "return config",
        "core.data = {'teve': 42}\n    logger.data = {'muha': 21}\n    client.data = {'id': 21}\n    return config")

    evf().upgrade()

    rev2 = evf().revision('test2', 'configpp://core.json&logger.json@app1')

    evf().upgrade()

    assert fs.get_data('/etc/app1/client.json') is None
