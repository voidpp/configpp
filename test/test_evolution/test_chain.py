import os
import pytest
from unittest.mock import patch
from configpp.evolution.chain import Chain, Revision, gen_rev_number, ChainException
from voidpp_tools.mocks.file_system import mockfs
from datetime import datetime

from .utils import FileSystem, mock_import

@pytest.fixture(scope = 'function')
def fs():
    template_file_path = Revision.ORIGINAL_TEMPLATE_FILE_PATH
    with open(template_file_path) as f:
        template_file_content = f.read()

    fs = FileSystem({
        'versions': {},
        'script.py.tmpl': template_file_content,
    })

    return fs

@pytest.fixture(scope = 'function')
def chain():
    return Chain('/versions')

def create_chain(fs, count = 4, message_template = 'teve{}') -> Chain:
    chain = Chain('/versions')
    with fs.mock():
        while len(chain) < count:
            chain.add(message_template.format(len(chain)), 'script.py.tmpl')
    return chain

@mockfs({'versions': {}})
def test_build_empty_chain(chain):

    chain.build()


def test_dump_and_load(fs: FileSystem, chain: Chain):

    rev = Revision('teve', 'ba79834caa9d', datetime(2018, 1, 1, 18, 42, 42))

    with fs.mock():
        chain.dump(rev, 'script.py.tmpl')

        with mock_import(fs):
            assert rev == chain.load(rev.filename)


def test_create_first_rev_on_chain(fs: FileSystem, chain: Chain):

    with fs.mock():
        chain.build()
        rev = chain.add('teve', 'script.py.tmpl')

        assert os.path.isfile(os.path.join('/versions', rev.filename))

        with mock_import(fs):
            rev2 = chain.load(rev.filename)
            assert rev == rev2


def test_build_chain(fs: FileSystem, chain: Chain):

    create_chain(fs)

    with fs.mock():
        with mock_import(fs):
            chain.build()
            messages = [rev.message for revid, rev in chain.links.items()]
            assert messages == ['teve3', 'teve2', 'teve1', 'teve0']


def test_chain_head_prop(fs: FileSystem):

    chain = create_chain(fs)

    revs = list(chain.links.keys())

    assert chain.head == revs[0]
    assert chain.head == revs[0]

def test_chain_tail_prop(fs: FileSystem):

    chain = create_chain(fs)

    revs = list(chain.links.keys())

    assert chain.tail == revs[-1]
    assert chain.tail == revs[-1]

@pytest.mark.parametrize('rev_str_or_idx, idx', [
    (0, 0),
    ('head', 0),
    ('tail', 9),
    ('head~1', 1),
    ('tail^1', 8),
])
def test_revparse(fs: FileSystem, rev_str_or_idx, idx):

    chain = create_chain(fs, 10)

    revs = list(chain.links.keys())

    rev_str = rev_str_or_idx if isinstance(rev_str_or_idx, str) else revs[rev_str_or_idx]

    assert chain.parse_revision(rev_str) == revs[idx]


@pytest.mark.parametrize('rev_str', [
    ('headd'),
    ('taill'),
    ('head~12'),
    ('tail^12'),
    (''),
    ('h23g4.2h3fg4'),
])
def test_revparse_bad_vals(fs: FileSystem, rev_str):

    chain = create_chain(fs, 2)

    with pytest.raises(ChainException):
        chain.parse_revision(rev_str)

def test_walk(fs: FileSystem):

    chain = create_chain(fs, 10)

    revs = list(chain.links.keys())

    walked_revs = list(chain.walk(revs[5], revs[1]))

    assert len(walked_revs) == 4
    assert walked_revs[0].id == revs[4]
    assert walked_revs[1].id == revs[3]
    assert walked_revs[2].id == revs[2]
    assert walked_revs[3].id == revs[1]
