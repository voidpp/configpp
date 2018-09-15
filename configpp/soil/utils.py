
import re
from importlib import import_module

from .group import Group, GroupMember
from .config import Config, ConfigBase
from .transform import YamlTransform, JSONTransform, guess_transform_for_file
from .transport import Transport
from .exception import SoilException


class SoilUriParserException(SoilException):
    pass

def import_class(uri: str):
    parts = uri.split(':')
    if len(parts) != 2:
        raise SoilUriParserException("Wrong class import format in '{}'".format(uri))

    return getattr(import_module(parts[0]), parts[1])

_config_pattern = re.compile('([\w.]+)(\?)?(%([\w.:]+))?')

def parse_config_definition(definition: str):
    res = _config_pattern.match(definition)
    if not res:
        raise SoilUriParserException("Wrong config def format in '{}'".format(definition))

    name, optional, _, transform = res.groups()
    transform_class = import_class(transform) if transform else guess_transform_for_file(name)

    if transform_class is None:
        raise SoilUriParserException("Cannot guess transform beacuse the file format is unknown, and there is no explicit transform for name: '{}'".format(name))

    return name, transform_class, optional is None

def create_from_url(url: str) -> ConfigBase:
    """Create config handler instances from url

    Example uris:
        configpp://app.json
        configpp://core.yaml%configpp.soil.transform:YamlTransform&logger.yaml%configpp.soil.transform:YamlTransform@app/configpp.soil.transport:Transport
        configpp://core.yaml&logger.yaml@app
    """
    res = re.match('configpp:\/\/([\w.:%&\?]+)(@[\w]+)?(/[\w.:]+)?(#[\w.:]+)?', url)
    if not res:
        raise SoilUriParserException("Wrong uri format")

    config_defs, group_name, transport, location = res.groups()

    transport_class = import_class(transport) if transport else Transport

    if group_name:

        members = []

        for config_def in config_defs.split('&'):

            name, transform_class, mandatory = parse_config_definition(config_def)

            members.append(GroupMember(name, transform_class(), mandatory))

        return Group(group_name[1:], members, transport_class())

    else:
        name, transform_class, _ = parse_config_definition(config_defs)
        return Config(name, transform_class(), transport_class())
