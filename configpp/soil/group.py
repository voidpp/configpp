import os
import logging
from typing import List, Dict
from collections import OrderedDict

from configpp.soil.config import ConfigFileBase, DEFAULT, ConfigBase
from configpp.soil.transport import Transport, Location
from configpp.soil.exception import SoilException
from configpp.soil.transform import TransformBase, JSONTransform

logger = logging.getLogger(__name__)

class GroupException(SoilException):
    pass

class GroupMember(ConfigFileBase):

    def __init__(self, name: str, transform: TransformBase = None, mandatory = True):
        super().__init__(name, transform or JSONTransform())
        self._mandatory = mandatory
        self._group_name = None

    @property
    def mandatory(self):
        return self._mandatory

    @property
    def relpath(self) -> str:
        return os.path.join(self._group_name, self._name)

    # the purpose of this method is hide the ConfigFileBase.dump function to prevent write to different locations
    def dump(self):
        self._direct_dump(self._location)

    # friendly class: Group
    def _update(self, group_name: str, location: Location = None):
        self._location = location
        self._group_name = group_name

    # friendly class: Group
    def _direct_dump(self, location: Location = None):
        super().dump(location)

    def __repr__(self):
        return "<GroupMember name={}, transform={}, mandatory={}>".format(self._name, self._transform.__class__.__name__, self._mandatory)


class Group(ConfigBase):
    """Group of config collected by the transport layer

    Args:
        TODO:
    """

    def __init__(self, name: str, configs: List[GroupMember], transport: Transport = None):
        super().__init__(name)
        self._transport = transport or Transport()
        self._configs = OrderedDict([(cfg.name, cfg) for cfg in configs]) # type: Dict[str, GroupMember]

    @property
    def transport(self):
        return self._transport

    @property
    def members(self) -> Dict[str, GroupMember]:
        return self._configs

    @property
    def is_loaded(self) -> bool:
        return self._location is not None

    def add_member(self, member: GroupMember):
        self._configs[member.name] = member

    def load(self) -> bool:
        logger.debug("Group load: with %s", list(self._configs.values()))
        self._transport.init_for(self._name)
        locations = self._transport.locations
        exists_reward = len(self._configs) + 1
        location_points = [0 for l in locations]
        logger.debug("Exists reward: %s", exists_reward)

        min_points = sum([exists_reward for config in self._configs.values() if config.mandatory])

        logger.debug("Minimum points to accept a location: %s", min_points)

        for idx, location in enumerate(locations):
            for config in self._configs.values():
                relpath = os.path.join(self._name, config.name)
                location.init_for(relpath)
                exists = location.check(relpath)
                if exists:
                    location_points[idx] += exists_reward
                elif not config.mandatory:
                    location_points[idx] += 1

        logger.debug("Group load: location points: %s", location_points)

        max_point = max(location_points)
        if max_point < min_points:
            logger.debug("Group load: target not found")
            return False

        self._location = locations[location_points.index(max_point)]

        logger.info("Group load: found location: %s", self._location)

        for config in self._configs.values():
            path = os.path.join(self._name, config.name)
            config._update(self._name, self._location)
            if self._location.check(path):
                config.load()
            else:
                logger.debug("Group load: %s data not found (optional)", config.name)

        return True

    def dump(self, location: Location = None) -> bool:
        for config in self._configs.values():
            config._update(self._name)
            config._direct_dump(location or self._location)


    def __repr__(self):
        return "<Group name={}, transport={}, members={}".format(self.name, self._transport.__class__.__name__, list(self.members.values()))
