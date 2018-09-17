import os
import re
import random
from datetime import datetime
import importlib.util
import importlib.machinery

from slugify import slugify

REVISION_NUMBER_LENGTH = 12

def gen_rev_number():
    start = int('0x1' + '0' * (REVISION_NUMBER_LENGTH-1), 16)
    end = int('0x'+ 'F' * REVISION_NUMBER_LENGTH, 16)
    return '{:x}'.format(random.randrange(start, end))

class Revision():

    FILENAME_PATTERN = re.compile('([a-f\d]{%s})_.+\.py' % REVISION_NUMBER_LENGTH)
    ORIGINAL_TEMPLATE_FILE_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'script.py.tmpl')

    def __init__(self, message: str, id: str, date: datetime = None, parent_id: str = '', handler = None):
        self._id = id
        self._message = message
        self._parent_id = parent_id
        self._date = date or datetime.now()
        self._handler = handler

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date

    @property
    def date_str(self):
        return self._date.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def parent_id(self):
        return self._parent_id

    @property
    def filename(self):
        return '{}_{}.py'.format(self._id, slugify(self._message))

    @property
    def message(self):
        return self._message

    def upgrade(self, *args):
        return self._handler.upgrade(*args)

    def downgrade(self, *args):
        return self._handler.downgrade(*args)

    def __eq__(self, other: 'Revision'):
        return self.id == other.id and self.date_str == other.date_str and self.message == other.message and self.parent_id == other.parent_id

    def __repr__(self):
        return "<Revision id: {}, message: {}, date: {}, parent: {}>".format(self.id, self.message, self.date_str, self.parent_id)
