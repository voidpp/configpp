import os
from unittest.mock import patch

from pytest import fixture, mark, raises

from configpp.evolution import Evolution, EvolutionException
from configpp.evolution.revision import Revision, gen_rev_number
from configpp.soil import YamlTransform
from voidpp_tools.mocks.file_system import mockfs

from .utils import FileSystem, mock_import, SpiderManTransform

@fixture()
def fs():

    template_file_path = Revision.ORIGINAL_TEMPLATE_FILE_PATH
    with open(template_file_path) as f:
        template_file_content = f.read()

    data = {
        'evolution': {
            'versions': {},
            'script.py.tmpl': template_file_content,
        }
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

@fixture(scope = 'module')
def yaml():
    return YamlTransform()


def test_generate_valid_rev():
    rev = gen_rev_number()
    filename = '%s_teve.py' % rev
    assert Revision.FILENAME_PATTERN.match(filename)

def test_first_rev_no_uri(fs, base_config):

    ev = Evolution()
    ev.load(base_config)

    assert ev.revision('test') is None

def test_write_config_file_after_first_revision_created_with_new_config(fs: FileSystem, base_config, yaml: YamlTransform):
    fs.set_data('/evolution.yaml', yaml.serialize(base_config))
    ev = Evolution()
    ev.load()

    ev.revision('test1', 'configpp://app.yaml')

    cfg_data = yaml.deserialize(fs.get_data('/evolution.yaml'))
    assert len(cfg_data['configpp_urls']) == 1
    assert 'head' in cfg_data['configpp_urls']
    assert cfg_data['configpp_urls']['head'] == 'configpp://app.yaml'


def test_write_config_file_after_nth_revision_created_with_new_config(fs: FileSystem, base_config, yaml: YamlTransform):
    fs.set_data('/evolution.yaml', yaml.serialize(base_config))
    ev = Evolution()
    ev.load()

    r1 = ev.revision('test1', 'configpp://app.yaml')
    r2 = ev.revision('test2', 'configpp://core.yaml&logger.json@app1')

    cfg_data = yaml.deserialize(fs.get_data('/evolution.yaml'))
    assert len(cfg_data['configpp_urls']) == 2
    assert 'head' in cfg_data['configpp_urls']
    assert r1.id in cfg_data['configpp_urls']
    assert cfg_data['configpp_urls']['head'] == 'configpp://core.yaml&logger.json@app1'

def test_first_rev_single_config(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)

    rev = ev.revision('test', 'configpp://app.yaml')

    data = fs.get_data('evolution/versions/' + rev.filename)

    revision_file_lines = data.split('\n')

    assert "from configpp.soil.transform import YamlTransform" in revision_file_lines
    assert "from configpp.soil.transport import Transport" in revision_file_lines
    assert "    config = Config('app.yaml', YamlTransform(), Transport())" in revision_file_lines
    assert "    return config" in revision_file_lines

def test_first_rev_group_config(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)

    rev = ev.revision('test', 'configpp://core.yaml&logger.json@app1')

    rev_file_data = fs.get_data('evolution/versions/' + rev.filename)

    revision_file_lines = rev_file_data.split('\n')

    assert "from configpp.soil.transform import JSONTransform, YamlTransform" in revision_file_lines
    assert "from configpp.soil.transport import Transport" in revision_file_lines
    assert "    core = GroupMember('core.yaml', YamlTransform())" in revision_file_lines
    assert "    logger = GroupMember('logger.json', JSONTransform())" in revision_file_lines
    assert "    config = Group('app1', [core, logger], Transport())" in revision_file_lines
    assert "    return config" in revision_file_lines

def test_single_config_not_changed(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)
    ev.revision('test1', 'configpp://app.yaml')

    rev = ev.revision('test2')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "from configpp.soil.transform import YamlTransform" in lines
    assert "from configpp.soil.transport import Transport" in lines
    assert "def upgrade(config: Config):" in lines

def test_group_config_not_changed(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)
    ev.revision('test1', 'configpp://core.yaml&logger.json@app1')

    rev = ev.revision('test2')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "from configpp.soil.transform import JSONTransform, YamlTransform" in lines
    assert "from configpp.soil.transport import Transport" in lines
    assert "def upgrade(core: GroupMember, logger: GroupMember, config: Group):" in lines

def test_single_config_change_to_group_config(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)

    ev.revision('test1', 'configpp://app1.yaml')

    rev = ev.revision('test2', 'configpp://core.yaml&logger.json@app1')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "from configpp.soil.transform import JSONTransform, YamlTransform" in lines
    assert "from configpp.soil.transport import Transport" in lines
    assert "def upgrade(config: Config):" in lines
    assert "    core = GroupMember('core.yaml', YamlTransform())" in lines
    assert "    logger = GroupMember('logger.json', JSONTransform())" in lines
    assert "    new_config = Group('app1', [core, logger], Transport())" in lines
    assert "    new_config.location = config.location" in lines
    assert "    return new_config" in lines

def test_group_config_add_new_member(fs: FileSystem, base_config):
    ev = Evolution()
    ev.load(base_config)

    ev.revision('test1', 'configpp://core.yaml&logger.json@app1')

    rev = ev.revision('test2', 'configpp://core.yaml&logger.json&clients.json@app1')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "    clients = GroupMember('clients.json', JSONTransform())" in lines
    assert "    clients.data = {} # put initial data here" in lines
    assert "    config.add_member(clients)" in lines

def test_group_config_del_member(fs: FileSystem, base_config):
    ev = Evolution()
    ev.load(base_config)

    ev.revision('test1', 'configpp://core.yaml&logger.json&clients.json@app1')

    rev = ev.revision('test2', 'configpp://core.yaml&logger.json@app1')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "    del config.members['clients.json']" in lines

def test_single_config_change_name(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)
    ev.revision('test1', 'configpp://app.yaml')

    rev = ev.revision('test2', 'configpp://app2.yaml')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "    config.name = 'app2.yaml'" in lines


def test_group_config_change_name(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)
    ev.revision('test1', 'configpp://core.yaml&logger.json@app1')

    rev = ev.revision('test2', 'configpp://core.yaml&logger.json@app2')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "    config.name = 'app2'" in lines

def test_group_config_member_change_transform(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)
    ev.revision('test1', 'configpp://core.yaml&logger.json@app1')

    rev = ev.revision('test2', 'configpp://core.yaml&logger.yaml@app1')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    print(data)

    assert "    logger.transform = YamlTransform()" in lines

def test_single_config_change_transform(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)
    ev.revision('test1', 'configpp://app.yaml')

    rev = ev.revision('test2', 'configpp://app.json')

    data = fs.get_data('evolution/versions/' + rev.filename)
    lines = data.split('\n')

    assert "    config.transform = JSONTransform()" in lines

def test_use_custom_transform_single_firts_rev(fs: FileSystem, base_config):

    ev = Evolution()
    ev.load(base_config)

    rev = ev.revision('test', 'configpp://app.yaml%test_evolution.utils:SpiderManTransform')

    data = fs.get_data('evolution/versions/' + rev.filename)

    revision_file_lines = data.split('\n')

    assert "from test_evolution.utils import SpiderManTransform" in revision_file_lines
    assert "    return config" in revision_file_lines
