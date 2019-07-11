
from configpp.tree import Tree, Settings

def test_load_convert_underscores_to_hypens():

    tree = Tree(Settings(convert_underscores_to_hypens = True))

    @tree.root()
    class Config():

        param_simpe_1 = int

    cfg = tree.load({'param-simpe-1': 42})

    assert cfg.param_simpe_1 == 42


def test_dump_convert_underscores_to_hypens():

    tree = Tree(Settings(convert_underscores_to_hypens = True))

    @tree.root()
    class Config():

        param_simpe_1 = 42

    cfg = tree.load({})
    cfg.param_simpe_1 = 84

    data = tree.dump(cfg)

    assert data == {'param-simpe-1': 84}


def test_dump_convert_underscores_to_hypens_and_camel_case_to_hypens():

    tree = Tree(Settings(convert_underscores_to_hypens = True, convert_camel_case_to_hypens = True))

    @tree.root()
    class Config():

        param_simpe_1 = 42

    cfg = tree.load({})
    cfg.param_simpe_1 = 84

    data = tree.dump(cfg)

    assert data == {'param-simpe-1': 84}


def test_load_convert_camel_case_to_hypens():

    tree = Tree(Settings(convert_camel_case_to_hypens = True))

    @tree.root()
    class Config():

        @tree.node()
        class TypicalClassName():

            param = int

    print(tree.build_schema())

    cfg = tree.load({'typical-class-name': {'param': 42}})

    assert cfg.TypicalClassName.param == 42


def test_dump_convert_camel_case_to_hypens():

    tree = Tree(Settings(convert_camel_case_to_hypens = True))

    @tree.root()
    class Config():

        @tree.node()
        class TypicalClassName():

            param = int

    cfg = tree.load({'typical-class-name': {'param': 42}})
    cfg.TypicalClassName.param = 84

    data = tree.dump(cfg)

    assert data == {'typical-class-name': {'param': 84}}

def test_dump_method_name_in_node_classes():

    tree = Tree(Settings(dump_method_name_in_node_classes = 'dump'))

    @tree.root()
    class Config():

        param_simpe_1 = 42

    cfg = tree.load({})

    assert cfg.dump() == {'param_simpe_1': 42}


def test_dump_method_name_in_node_classes_sub():

    tree = Tree(Settings(dump_method_name_in_node_classes = 'dump'))

    @tree.root()
    class Config():

        @tree.node()
        class node1():

            param = int

    cfg = tree.load({'node1': {'param': 42}})

    assert cfg.dump() == {'node1': {'param': 42}}
    assert cfg.node1.dump() == {'param': 42}
