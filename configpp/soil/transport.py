import logging
import os
from typing import List

logger = logging.getLogger(__name__)

class Location():

    def __init__(self, base_path: str):
        self._base_path = base_path

    def init_for(self, path: str):
        pass

    @property
    def valid(self):
        return os.path.exists(self._base_path)

    def target_path(self, path: str):
        return os.path.join(self._base_path, path)

    def check(self, path: str):
        return os.path.isfile(self.target_path(path))

    def read(self, path: str):
        with open(self.target_path(path)) as f:
            return f.read()

    def remove(self, path: str) -> bool:
        target = self.target_path(path)
        if not os.path.isfile(target):
            return False
        os.remove(target)
        return True

    def write(self, path: str, data) -> bool:
        target = self.target_path(path)
        logger.debug("write data to '%s'", target)
        target_dir = os.path.dirname(target)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(target, 'w') as f:
            f.write(data)
        return True

    def __repr__(self):
        return "<Location: '{}'>".format(self._base_path)

class ClimberLocation(Location):
    """Climbs up in the folder tree from the start_path

    TODO
    """

    def __init__(self, start_path: str = None):
        super().__init__(start_path or os.getcwd())
        self._found_path = None

    def init_for(self, path: str):
        parts = self._base_path.split(os.sep)

        for idx in range(len(parts), 0, -1):
            try_base_path = os.sep.join(parts[:idx])
            if os.path.isfile(os.path.join(try_base_path, path)):
                self._found_path = try_base_path
                break

    @property
    def valid(self):
        return self._found_path is not None

    def target_path(self, path: str):
        return os.path.join(self._found_path, path)

    def __repr__(self):
        return "<ClimberLocation: {}>".format(self._found_path)

class Transport():
    """Make the connection with the file system

    TODO
    """

    def __init__(self, locations: List[Location] = None, env_var_name = 'CONFIGPP_CONFIG_LOCATION'):
        self._locations = locations or [
            # Location(os.getenv(env_var_name, '')), # 'Invalid location' error message is generated if env_var_name is not found
            Location(os.getcwd()),
            Location(os.path.expanduser('~')),
            Location('/etc'),
        ]

    def init_for(self, path: str):
        for location in self._locations:
            location.init_for(path)
            if not location.valid:
                logger.error("Invalid location: %r", location)

    @property
    def locations(self):
        return self._locations


class ClimberTransport(Transport):
    """Shorthand transport class to use ClimberLocation
    """

    def __init__(self):
        super().__init__([ClimberLocation()])
