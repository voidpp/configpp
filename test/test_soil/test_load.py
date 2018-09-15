
from configpp.soil import Config, Group, GroupMember, Transport, ClimberLocation
from voidpp_tools.mocks.file_system import FileSystem, mockfs


_data_filename = 'test1.json'
_data = {_data_filename: '{"a": 42}'}

def test_load_simple_not_found():
    cfg = Config(_data_filename)

    assert cfg.load() is False

@mockfs({'etc': _data})
def test_load_simple_found_etc():

    cfg = Config(_data_filename)

    assert cfg.load() is True

    assert cfg.data == {"a": 42}
    assert cfg.path == '/etc/' + _data_filename


@mockfs({'home': {'douglas': _data}})
def test_load_simple_found_home():

    cfg = Config(_data_filename)

    assert cfg.load() is True

    assert cfg.data == {"a": 42}

@mockfs({'teve': _data}, cwd = '/teve')
def test_load_simple_found_cwd():

    cfg = Config(_data_filename)

    assert cfg.load() is True

    assert cfg.data == {"a": 42}

@mockfs({'etc': _data, 'home': {'douglas': {_data_filename: '{"a": 84}'}}})
def test_load_simple_location_order():

    cfg = Config(_data_filename)

    assert cfg.load() is True
    assert cfg.data == {"a": 84}

@mockfs({'etc': {'test1': {'core.json': '{"a": 42}', 'logger.json': '{"b": 42}'}}})
def test_load_group():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json')

    grp = Group('test1', [core, logger])

    assert grp.load()
    assert core.data == {"a": 42}
    assert logger.data == {"b": 42}

@mockfs({'etc': {'test1': {'logger.json': '{"b": 42}'}}})
def test_cant_load_group_missing_one():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json')

    grp = Group('test1', [core, logger] + [GroupMember('op%s' % i, mandatory=False) for i in range(10)])

    assert grp.load() is False


@mockfs({'etc': {'test1': {'logger.json': '{"b": 42}'}}})
def test_cant_load_group_missing_many():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json')

    grp = Group('test1', [core, logger])

    assert grp.load() is False


@mockfs({'etc': {'app.json': '{"a": 42}'}})
def test_load_group_single():

    core = GroupMember('app.json')

    grp = Group('', [core])

    assert grp.load()
    assert core.data == {"a": 42}

@mockfs({'etc': {'test1': {'core.json': '{"a": 42}'}}})
def test_load_group_optional():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json', mandatory = False)

    grp = Group('test1', [core, logger])

    assert grp.load() is True
    assert core.data == {"a": 42}
    assert core.path == '/etc/test1/core.json'
    assert logger.is_loaded is False

@mockfs({
    'home': {
        'douglas': {
            'test1': {
                'core.json': '{"a": 21}'
            }
        }
    },
    'etc': {
        'test1': {
            'core.json': '{"a": 42}',
            'logger.json': '{"b": 42}',
        }
    }
})
def test_load_group_optional_full_group_is_more_imporant_than_location_order():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json', mandatory = False)

    grp = Group('test1', [core, logger])

    assert grp.load() is True
    assert core.data == {"a": 42}
    assert logger.is_loaded
    assert logger.data == {"b": 42}

@mockfs({'home': {'douglas': {'teve': {_data_filename: '{"a": 84}'}}}}, cwd = '/home/douglas/teve/muha/subn')
def test_load_simple_climber():

    cfg = Config(_data_filename, transport = Transport([ClimberLocation()]))

    assert cfg.load() is True

    assert cfg.data == {"a": 84}
    assert cfg.path == '/home/douglas/teve/' + _data_filename


@mockfs({'home': {'douglas': {'teve': {'test1': {'core.json': '{"a": 42}', 'logger.json': '{"b": 42}'}}}}}, cwd = '/home/douglas/teve/muha/subn')
def test_load_group_climber_loc():

    core = GroupMember('core.json')
    logger = GroupMember('logger.json')

    grp = Group('test1', [core, logger], transport = Transport([ClimberLocation()]))

    assert grp.load()
    assert core.data == {"a": 42}
    assert logger.data == {"b": 42}
    assert grp.path == '/home/douglas/teve/test1'
    assert core.path == '/home/douglas/teve/test1/core.json'
