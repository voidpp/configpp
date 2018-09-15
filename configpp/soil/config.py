from abc import ABC, abstractproperty, abstractmethod
import logging

from configpp.soil.transform import TransformBase, JSONTransform
from configpp.soil.transport import Transport, Location
from configpp.soil.exception import SoilException

logger = logging.getLogger(__name__)

DEFAULT = object()

class ConfigBase():

    def __init__(self, name: str):
        self._name = name
        self._location = None # type: Location

    @abstractproperty
    def is_loaded(self) -> bool:
        """the config is loaded or not"""

    @abstractmethod
    def load(self) -> bool:
        """load the stuffs"""

    @abstractmethod
    def dump(self, location: Location = None) -> bool:
        """dump the stuffs"""

    @property
    def relpath(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._location.target_path(self.relpath)

    @property
    def name(self) -> str:
        return self._name

    @property
    def location(self) -> Location:
        return self._location

    @location.setter
    def location(self, loc: Location):
        self._location = loc

class ConfigFileBase(ConfigBase):
    """Class to define a config format and others

    Args:
        name:
        transform:
    """

    def __init__(self, name: str, transform: TransformBase):
        super().__init__(name)
        self._transform = transform
        self._data = None
        self._is_loaded = False

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._is_loaded = True

    def process_data(self, raw_data):
        self.data = self._transform.deserialize(raw_data)

    def serialize(self):
        return self._transform.serialize(self.data)

    @property
    def is_loaded(self):
        return self._is_loaded

    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, val: TransformBase):
        self._transform = val

    def load(self) -> bool:
        if self._location is None:
            raise SoilException("Location is none, config cannot be loaded! %r", self)
        raw_data = self._location.read(self.relpath)
        logger.debug("Config load: %s data len: %d", self._name, len(raw_data))
        self.process_data(raw_data)
        return self._is_loaded

    def dump(self, location: Location = None) -> bool:
        loc = location or self._location
        if loc is None:
            logger.error("Cannot dump config because no location!")
            return False
        return loc.write(self.relpath, self._transform.serialize(self._data))

    def remove(self) -> bool:
        if self._location is None:
            return False
        return self._location.remove(self.relpath)

    def __repr__(self):
        return "<Config name: '{}', transform: {}, data: {}>".format(self._name, self._transform, self._data)

class Config(ConfigFileBase):
    """Class to define a config entity with location, format and others

    Args:
        TODO
    """

    def __init__(self, name: str, transform: TransformBase = None, transport: Transport = None):
        super().__init__(name, transform or JSONTransform())
        self._transport = transport or Transport()
        logger.debug("Config initialized: %r", self)

    @property
    def transport(self):
        return self._transport

    def load(self) -> bool:
        self._transport.init_for(self._name)
        for location in self._transport.locations:
            if location.check(self._name):
                self._location = location
                logger.info("Config: load: found at %s", location.target_path(self._name))
                break
        else:
            logger.info("Config: load: not found")
            return False

        return super().load()
