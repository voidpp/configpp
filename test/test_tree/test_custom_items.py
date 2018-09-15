
from enum import Enum, IntEnum
from configpp.tree import Tree
from datetime import datetime

def test_load_datetime_default():
    tree = Tree()

    @tree.root()
    class Config():

        param_leaf_1 = datetime(2018, 4, 2, 14, 42, 12)

    cfg = tree.load({})

    assert cfg.param_leaf_1.day == 2


def test_load_datetime():
    tree = Tree()

    @tree.root()
    class Config():

        param_leaf_1 = datetime

    cfg = tree.load({'param_leaf_1': '2018-04-02 14:42:42'})

    assert cfg.param_leaf_1.day


def test_datetime_dump():
    tree = Tree()

    @tree.root()
    class Config():

        param_leaf_1 = datetime

    cfg = tree.load({'param_leaf_1': '2018-04-02 14:42:42'})

    cfg.param_leaf_1 = cfg.param_leaf_1.replace(day = 8)

    data = tree.dump(cfg)

    assert data['param_leaf_1'] == '2018-04-08T14:42:42'


def test_load_enum():

    class Animal(Enum):

        CAT = 'cat'
        DOG = 'dog'
        PLATYPUS = 'platypus'

    tree = Tree()

    @tree.root()
    class Config():

        param = Animal

    cfg = tree.load({'param': 'cat'})

    assert cfg.param == Animal.CAT

def test_dump_enum():

    class Animal(Enum):

        CAT = 'cat'
        DOG = 'dog'
        PLATYPUS = 'platypus'

    tree = Tree()

    @tree.root()
    class Config():

        param = Animal

    cfg = tree.load({'param': 'cat'})

    cfg.param = Animal.PLATYPUS

    data = tree.dump(cfg)

    assert data == {'param': 'platypus'}

def test_load_enum_default():

    class Animal(Enum):

        CAT = 'cat'
        DOG = 'dog'
        PLATYPUS = 'platypus'

    tree = Tree()

    @tree.root()
    class Config():

        param = Animal.CAT

    cfg = tree.load({})

    assert cfg.param == Animal.CAT

def test_load_int_enum():

    class Camel(IntEnum):

        ONE = 1
        TWO = 2

    tree = Tree()

    @tree.root()
    class Config():

        param = Camel

    cfg = tree.load({'param': 1})

    assert cfg.param == Camel.ONE