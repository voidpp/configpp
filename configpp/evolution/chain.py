import re
import os
import importlib.util
import importlib.machinery
import logging
from collections import OrderedDict
from dateutil import parser
from typing import Dict, Generator
from enum import IntEnum

from .utils import import_file
from .revision import Revision, gen_rev_number
from .exceptions import EvolutionException

class ChainException(EvolutionException):
    pass

logger = logging.getLogger(__name__)

class Chain():

    def __init__(self, folder: str):
        self._folder = folder
        self._links = OrderedDict() # type: Dict[str, Revision]
        self._named_revisions_pattern = re.compile('([\w]+)((~|\^)([\d]{1,}))?')

    @property
    def head(self) -> str:
        return next(iter(self._links)) if self._links else ''

    @property
    def tail(self) -> str:
        return next(reversed(self._links)) if self._links else ''

    @property
    def links(self):
        return self._links

    def walk(self, old_rev: str = 'tail', new_rev: str = 'head', include_old = False) -> Generator[Revision, None, None]:
        """Gives back the revisions, older first."""
        emit = False
        new_rev = self.parse_revision(new_rev)
        old_rev = self.parse_revision(old_rev)
        logger.debug("Walk from %s to %s", old_rev, new_rev)
        for id, rev in reversed(self._links.items()):

            if emit:
                yield rev

            if id == old_rev:
                emit = True
                if include_old:
                    yield rev

            if id == new_rev:
                return

    def parse_revision(self, revision: str):
        revision = revision.lower()

        res = self._named_revisions_pattern.match(revision)

        if not res:
            raise ChainException("Unknown revision '{}'".format(revision))

        ref, _, direction, diff = res.groups()

        rev = None

        if ref == 'head':
            rev = self.head
        elif ref == 'tail':
            rev = self.tail
        elif ref in self._links:
            rev = ref
        else:
            raise ChainException("Unknown revision '{}' because the ref part is unknown '{}'".format(revision, ref))

        if direction is None:
            return rev

        revs = list(self._links.keys())

        rev_idx = revs.index(rev)

        if direction == '~':
            rev_idx += int(diff)
        else:
            rev_idx -= int(diff)

        if rev_idx < 0 or rev_idx >= len(revs):
            raise ChainException("Cannot parse rev '{}', too much diff!".format(revision))

        return revs[rev_idx]

    def __len__(self):
        return len(self._links)

    def __contains__(self, key):
        return key in self._links

    def load(self, filename) -> Revision:
        rev_module = import_file(os.path.join(self._folder, filename))

        date = parser.parse(rev_module.date)
        return Revision(rev_module.message, rev_module.revision_id, date, rev_module.parent_id, rev_module)

    def build(self):
        revs = {}
        genesis_rev = None

        self._links.clear()

        for name in os.listdir(self._folder):
            res = Revision.FILENAME_PATTERN.match(name)
            if not res:
                continue

            rev = self.load(name)

            if not rev.parent_id:
                if genesis_rev is not None:
                    raise Exception('whoa!')
                genesis_rev = rev
            else:
                revs[rev.parent_id] = rev

        def add_to_chain(rev: Revision):
            self._links[rev.id] = rev
            logger.debug("Add revision to chain: %s", rev)
            if rev.id in revs:
                add_to_chain(revs[rev.id])

        if genesis_rev:
            add_to_chain(genesis_rev)

        self._links = OrderedDict(reversed(self._links.items()))

    def create_new_rev_number(self) -> str:
        while 1:
            rev_hex = gen_rev_number()
            if rev_hex not in self._links:
                return rev_hex

    def add(self, message: str, template_path: str, extra_params: dict = {}) -> Revision:
        rev_id = self.create_new_rev_number()
        parent_rev_id = self.head

        logger.debug("New unique revision number has been created: %s", rev_id)

        rev = Revision(message, rev_id, parent_id = parent_rev_id)

        self._links[rev_id] = rev
        self._links.move_to_end(rev_id, last = False) # pylint: disable=E1101
        # https://github.com/PyCQA/pylint/issues/1872

        logger.debug("Add new revision to chain: %s", rev)

        self.dump(rev, template_path, extra_params)

        return rev

    def dump(self, rev: Revision, template_path: str, extra_params: dict = {}) -> str:

        data = {
            'message': rev.message,
            'date': rev.date_str,
            'revision_id': rev.id,
            'parent_id': rev.parent_id,
            'extra_imports': '',
            'upgrade_args': '',
            'downgrade_args': '',
            'upgrade_ops': '',
            'downgrade_ops': '',
        }

        data.update(extra_params)

        with open(template_path) as f:
            template_content = f.read()

        path = os.path.join(self._folder, rev.filename)

        content = template_content.format(**data)

        logger.debug("Revision %s is serialized: \n%s", rev.id, content)

        with open(path, 'w') as f:
            f.write(content)

        logger.info("Revision %s dumped to: %s", rev.id, path)

        return path
