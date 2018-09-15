
from voidpp_tools.mocks.file_system import FileSystem, mockfs
from configpp.soil.transport import ClimberLocation

_data_filename = 'test1.json'

@mockfs({'home': {'douglas': {'devel': {_data_filename: '{"a": 84}', 'teve': {}}}}})
def test_climber_location_basic():

    loc = ClimberLocation('/home/douglas/devel/teve')

    loc.init_for(_data_filename)

    assert loc.target_path(_data_filename) == '/home/douglas/devel/' + _data_filename

@mockfs({'home': {'douglas': {'devel': {_data_filename: '{"a": 84}'}}}})
def test_climber_location_same_folder():

    loc = ClimberLocation('/home/douglas/devel')

    loc.init_for(_data_filename)

    assert loc.target_path(_data_filename) == '/home/douglas/devel/' + _data_filename
