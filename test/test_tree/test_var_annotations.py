from pytest import raises
from configpp.tree import Tree
from copy import deepcopy
from typing import List, Dict

from voluptuous import MultipleInvalid

def test_schema_var_annotation_primitive_type():

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1: int

    schema = tree.build_schema()

    data = {'param_simpe_1': 42}

    assert schema(data) == data

    with raises(MultipleInvalid):
        assert schema({})

def test_schema_var_annotation_list():

    StringList = List[str]

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1: StringList

    schema = tree.build_schema()

    data = {'param_simpe_1': ['teve']}

    assert schema(data) == data

    with raises(MultipleInvalid):
        schema({})
    with raises(MultipleInvalid):
        schema({'param_simpe_1': 42})
    with raises(MultipleInvalid):
        schema({'param_simpe_1': [42]})

def test_schema_var_annotation_dict():

    StringDict = Dict[str, int]

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1: StringDict

    schema = tree.build_schema()

    data = {'param_simpe_1': {'teve': 42}}

    assert schema(data) == data

    with raises(MultipleInvalid):
        assert schema({})
    with raises(MultipleInvalid):
        assert schema({'param_simpe_1': {'k1': 'v1'}})

def test_load_simple_param_var_annotation():

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1: int

    cfg = tree.load({'param_simpe_1': 42})

    assert cfg.param_simpe_1 == 42

def test_repeated_schema_generation():

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1: int

    tree.build_schema()
    schema = tree.build_schema()
    assert len(schema.schema) == 1
