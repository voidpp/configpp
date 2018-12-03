
import re
from copy import copy
from typing import List

from voluptuous import MatchInvalid, Schema, Required

from .items import UNDEFINED, LeafBase


class DatabaseLeaf(LeafBase):

    _pattern = re.compile(r'([a-z0-9\+]{1,})://([^:]+):([^@]+)@(([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]).([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])|[-a-zA-Z0-9@%._\+~#=]{2,256}(\.[a-z]{2,6})?\b([-a-zA-Z0-9@%_\+.~#?&//=]*)|[a-zA-Z_-]*):?(\d*)?/([a-zA-Z_\d]+)')
    _sqlite_pattern = re.compile(r'sqlite(\+[a-z_0-9]{1,})?:\/\/\/(.+)')

    driver = None # type: str
    host = None # type: str
    port = None # type: int
    username = None # type: str
    password = None # type: str
    name = None # type: str

    uri = None # type: str

    @classmethod
    def _get_match(cls, value):
        match = cls._pattern.match(value)
        if not match:
            match = cls._sqlite_pattern.match(value)
        return match

    @classmethod
    def get_validator(cls):
        def validator(val):
            match = cls._get_match(val)
            if not match:
                raise MatchInvalid("wrong database format")

            return DatabaseLeaf(val)

        return validator

    def __init__(self, uri = None):

        if uri:
            groups = self._get_match(uri).groups()

            if groups[0] is None or groups[0].startswith('+'):
                self.driver = 'sqlite'
                if groups[0]:
                    self.driver += groups[0]
                self.name = groups[1]
            else:
                self.driver = groups[0]
                self.host = groups[3]
                self.port = groups[10]
                self.username = groups[1]
                self.password = groups[2]
                self.name = groups[11]

            self.uri = uri

    def __str__(self):
        data = copy(self.__dict__)
        data.update(
            auth = '{}:{}@'.format(self.username, self.password) if (self.username and self.password) else '',
            port = ':{}'.format(self.port) if self.port else '',
        )
        return '{driver}://{auth}{host}{port}/{name}'.format(**data)

class PythonLoggerLeaf(LeafBase):

    @classmethod
    def get_validator(cls):
        return Schema({
            'disable_existing_loggers': bool,
            'formatters': Schema({
                str: dict,
            }),
            'handlers': Schema({
                str: Schema({
                    Required('class'): str,
                    Required('formatter'): str,
                    'level': str,
                }, extra = True),
            }),
            'loggers': Schema({
                str: Schema({
                    'handlers': list,
                    'level': str,
                    'propagate': bool,
                }, required = True),
            }),
            'version': int,
        })
