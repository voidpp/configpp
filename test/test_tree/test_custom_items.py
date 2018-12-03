
from enum import Enum, IntEnum
from configpp.tree import Tree
from datetime import datetime
from configpp.tree.custom_items import DatabaseLeaf, PythonLoggerLeaf

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

def test_load_database():

    tree = Tree()

    @tree.root()
    class Config():

        param = DatabaseLeaf

    print(tree.build_schema())

    cfg = tree.load({'param': 'teve://user:pass@domain.hu/dbname'}) # type: Config

    assert cfg.param.driver == 'teve'
    assert cfg.param.username == 'user'
    assert cfg.param.password == 'pass'
    assert cfg.param.host == 'domain.hu'
    assert cfg.param.name == 'dbname'
    assert not cfg.param.port
    assert cfg.param.uri == 'teve://user:pass@domain.hu/dbname'

def test_load_database_sqlite():

    tree = Tree()

    @tree.root()
    class Config():

        param = DatabaseLeaf

    print(tree.build_schema())

    cfg = tree.load({'param': 'sqlite:///teve.db'}) # type: Config

    assert cfg.param.driver == 'sqlite'
    assert cfg.param.name == 'teve.db'
    assert cfg.param.uri == 'sqlite:///teve.db'


def test_load_logger_config():

    tree = Tree()

    @tree.root()
    class Config():

        param = PythonLoggerLeaf

    print(tree.build_schema())

    data = {
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "DEBUG"
            },
        },
        "loggers": {
            "teve": {
                "handlers": [
                    "console"
                ],
                "level": "DEBUG",
                "propagate": True
            },
        },
        "version": 1
    }

    cfg = tree.load({'param': data}) # type: Config

    assert cfg.param == data
