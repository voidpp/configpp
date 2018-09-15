import os
import logging
import json
from abc import ABC, abstractmethod
from collections import OrderedDict
from ruamel import yaml

from configpp.soil.exception import SoilException

logger = logging.getLogger(__name__)

class TransformException(SoilException):
    pass

_transform_extensions = {}

def extensions(*args):
    def decor(cls):
        for ext in args:
            _transform_extensions[ext] = cls
        return cls
    return decor

class TransformBase(ABC):
    """Base class for the different serializing methods, eg json or yaml"""

    @abstractmethod
    def serialize(self, data):
        """Make string from python data

        Args:
            data: any serializable python type

        Returns:
            The serialized string
        """

    @abstractmethod
    def deserialize(self, data: str):
        """Make python type from string

        Args:
            data (str): the raw string

        Returns:
            any serializable python type
        """

@extensions('json')
class JSONTransform(TransformBase):
    """Transform for json formatted data"""

    def serialize(self, data):
        return json.dumps(data)

    def deserialize(self, data: str):
        return json.loads(data, object_pairs_hook = OrderedDict)

@extensions('yaml', 'yml')
class YamlTransform(TransformBase):

    # very big TODO: mintha a default_flow_style-nak nem lenne hatasa... (test_write_config_file_after_nth_revision_created_with_new_config)

    def serialize(self, data):
        yaml.representer.RoundTripRepresenter.add_representer(OrderedDict, yaml.representer.RoundTripRepresenter.represent_dict)
        return yaml.dump(data, Dumper = yaml.RoundTripDumper, default_flow_style = False)

    def deserialize(self, data: str):
        return yaml.load(data, Loader = yaml.RoundTripLoader)


def guess_transform_for_file(filename):
    name, ext = os.path.splitext(filename)
    return _transform_extensions.get(ext[1:])
