
from enum import Enum
from datetime import datetime
from dateutil.parser import parse
from voluptuous import Invalid, Any

from .item_factory import LeafFactory, UNDEFINED

class DateTimeLeafFactory(LeafFactory):

    def create_schema(self):
        def validator(val):
            try:
                return val if isinstance(val, datetime) else parse(val)
            except (ValueError, TypeError) as e:
                raise Invalid(str(e))
        return validator

    def dump(self, value):
        return value.isoformat()

class EnumLeafFactory(LeafFactory):

    def create_schema(self):
        def validator(val):
            if isinstance(val, self._validator):
                return val
            values = {i.value: i for i in self._validator}
            if val not in values:
                raise Invalid("'%s' is not a valid choice of %s" % (val, list(values.keys())))
            return values[val]
        return validator

    def dump(self, value):
        return value.value
