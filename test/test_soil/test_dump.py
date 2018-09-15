
import os
from configpp.soil import Config, Group, GroupMember, Location
from voidpp_tools.mocks.file_system import FileSystem, mockfs


_data_filename = 'test1.json'
_data = {_data_filename: '{"a": 42}'}

@mockfs({'etc': {}})
def test_not_loaded_single_config_dump():

    cfg = Config(_data_filename)

    cfg.data = {"a": 42}

    cfg.dump(Location('/etc'))

    assert os.path.exists('/etc/test1.json')

@mockfs({'etc': _data})
def test_loaded_single_config_dump():

    cfg = Config(_data_filename)

    assert cfg.load()

    cfg.data['a'] = 43

    cfg.dump()

    with open('/etc/'+_data_filename) as f:
        content = f.read()

    assert content == '{"a": 43}'

@mockfs({'etc': {'test1': {'core.json': '{"a": 42}', 'logger.json': '{"b": 42}'}}})
def test_loaded_group_config_partial_dump():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json')

    grp = Group('test1', [core, logger])

    assert grp.load()

    core.data['a'] = 43

    core.dump()

    with open('/etc/test1/core.json') as f:
        content = f.read()

    assert content == '{"a": 43}'

@mockfs({'etc': {'test1': {'core.json': '{"a": 42}'}}})
def test_partially_loaded_group_config_partial_dump():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json', mandatory = False)

    grp = Group('test1', [core, logger])

    assert grp.load()

    logger.data = {'b': 84}

    logger.dump()

    with open('/etc/test1/logger.json') as f:
        content = f.read()

    assert content == '{"b": 84}'

@mockfs({'etc': {'test1': {'core.json': '{"a": 42}', 'logger.json': '{"b": 42}'}}})
def test_loaded_group_config_full_dump():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json')

    grp = Group('test1', [core, logger])

    assert grp.load()

    core.data['a'] = 43
    logger.data['b'] = 43

    grp.dump()

    with open('/etc/test1/core.json') as f:
        content_core = f.read()

    with open('/etc/test1/logger.json') as f:
        content_logger = f.read()

    assert content_core == '{"a": 43}'
    assert content_logger == '{"b": 43}'

@mockfs({'etc': {'test1': {'core.json': '{"a": 42}', 'logger.json': '{"b": 42}'}}})
def test_loaded_group_config_partial_direct_dump():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json')

    grp = Group('test1', [core, logger])

    assert grp.load()

    core.data = {'a': 84}
    core.dump()

    with open('/etc/test1/core.json') as f:
        content = f.read()

    assert content == '{"a": 84}'
