from pytest import raises, mark
from configpp.tree import Tree, ConfigTreeBuilderException, NodeBase
from copy import deepcopy
from typing import List, Dict

from voluptuous import MultipleInvalid, Range, All

def test_missing_root():
    tree = Tree()

    with raises(ConfigTreeBuilderException):
        tree.build_schema()

class ExampleServerConfig(NodeBase):

    host = str
    port = int

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def serialize(self):
        return self.__dict__

@mark.parametrize('default, other', [
    (42, 84),
    ('teve', 'muha'),
])
def test_optional_simple_param_with_default_value(default, other):

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = default

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    assert schema({}) == {'param_simpe_1': default}
    assert schema({'param_simpe_1': other}) == {'param_simpe_1': other}
    with raises(MultipleInvalid):
        assert schema({'param_simpe_2': other})


@mark.parametrize('type, value', [
    (int, 42),
    (str, 'teve'),
    (ExampleServerConfig, ExampleServerConfig('teve', 42).serialize())
])
def test_required_simple_param(type, value):

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = type

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    assert schema({'param_simpe_1': value}) == {'param_simpe_1': value}
    with raises(MultipleInvalid):
        assert schema({})
    with raises(MultipleInvalid):
        assert schema({'param_simpe_2': value})

def test_optional_and_required():

    tree = Tree()

    @tree.root()
    class Config():

        param1 = 42
        param2 = str

    schema = tree.build_schema()
    with raises(MultipleInvalid):
        assert schema({})
    with raises(MultipleInvalid):
        assert schema({'param1': 84})

    assert schema({'param2': 'teve'}) == {'param2': 'teve', 'param1': 42}

def test_list_param_required():
    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = [int]

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    assert schema({'param_simpe_1': [42]}) == {'param_simpe_1': [42]}
    assert schema({'param_simpe_1': []}) == {'param_simpe_1': []}
    with raises(MultipleInvalid):
        assert schema({'param_simpe_1': 42})
    with raises(MultipleInvalid):
        assert schema({})
    with raises(MultipleInvalid):
        assert schema({'param_simpe_1': ['teve']})


def test_list_param_optional():
    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = tree.list_node([int], [])

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    assert schema({'param_simpe_1': [42]}) == {'param_simpe_1': [42]}
    assert schema({}) == {'param_simpe_1': []}
    with raises(MultipleInvalid):
        assert schema({'param_simpe_1': ['teve']})

def test_list_param_default_only_values():
    tree = Tree()

    @tree.root()
    class Config():

        param = [1, 2, 3]

    schema = tree.build_schema()
    assert schema({}) == {'param': [1, 2, 3]}
    with raises(MultipleInvalid):
        schema({'param': ['teve']})

def test_list_param_default():
    tree = Tree()

    @tree.root()
    class Config():

        param = [1, 2, str]

    schema = tree.build_schema()
    assert schema({'param': [1, 'teve']}) == {'param': [1, 'teve']}


def test_list_param_default_only_values_various_types():
    tree = Tree()

    @tree.root()
    class Config():

        param = [1, 2, 'teve']

    schema = tree.build_schema()
    assert schema({}) == {'param': [1, 2, 'teve']}
    with raises(MultipleInvalid):
        schema({'param': [1.2]})

def test_detailed_leaf():

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = tree.leaf(All(int, Range(min = 0)))

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    assert schema({'param_simpe_1': 7}) == {'param_simpe_1': 7}

    with raises(MultipleInvalid):
        schema({})
    with raises(MultipleInvalid):
        schema({'param_simpe_1': -1})

def test_node_basics():

    tree = Tree()

    @tree.root()
    class Config():

        @tree.node()
        class param_node_1():
            host = str
            port = int

    source_data = {'param_node_1': {'host': 'teve', 'port': 42}}

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    with raises(MultipleInvalid):
        assert schema({})
    with raises(MultipleInvalid):
        assert schema({'param_node_1': 42})
    assert schema(source_data) == source_data

def test_node_basics_with_defaults_only():

    tree = Tree()

    @tree.root()
    class Config():

        @tree.node()
        class node1():

            @tree.node()
            class node2():
                param1 = 42
                param2 = ''

    schema = tree.build_schema()

    assert schema({}) == {'node1': {'node2': {'param1': 42, 'param2': ''}}}

def test_node_external_class():

    tree = Tree()

    class ServerConfig():
        host = str
        port = int

    @tree.root()
    class Config():

        param_node_1 = tree.node()(ServerConfig)

    source_data = {'param_node_1': {'host': 'teve', 'port': 42}}

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    with raises(MultipleInvalid):
        assert schema({'param_node_1': 42})
    assert schema(source_data) == source_data

def test_node_external_class_reuse():

    tree = Tree()

    class ServerConfig():
        host = str
        port = int

    @tree.root()
    class Config():

        server_config_1 = tree.node()(ServerConfig)
        server_config_2 = tree.node()(ServerConfig)

    source_data = {'server_config_1': {'host': 'teve', 'port': 42}, 'server_config_2': {'host': 'teve', 'port': 42}}

    schema = tree.build_schema()

    assert len(schema.schema) == 2
    with raises(MultipleInvalid):
        assert schema({'param_node_1': 42})
    assert schema(source_data) == source_data

def test_simple_param_class_instance():

    tree = Tree()

    @tree.root()
    class Config():

        param_node_1 = ExampleServerConfig('teve', 42)

    source_data = {'param_node_1': {'host': 'teve', 'port': 42}}

    schema = tree.build_schema()
    print(schema)

    assert len(schema.schema) == 1
    assert schema({}) == source_data
    assert schema(source_data) == source_data

def test_node_go_deep():

    tree = Tree()

    @tree.root()
    class Config():

        @tree.node()
        class oidc():
            config_url = str

            @tree.node()
            class credential():
                client_id = str
                key = str

    source_data = {'oidc': {'config_url': 'teve', 'credential': {'client_id': 'muha', 'key': 'da_key'}}}

    schema = tree.build_schema()

    assert len(schema.schema) == 1
    with raises(MultipleInvalid):
        assert schema({'oidc': 42})
    with raises(MultipleInvalid):
        assert schema({'oidc': {}})
    with raises(MultipleInvalid):
        assert schema({'oidc': {'config_url': 'dd'}})

    assert schema(source_data) == source_data

def test_dict_node():

    tree = Tree()

    @tree.root()
    class Config():

        servers = tree.dict_node(str, ExampleServerConfig)

    schema = tree.build_schema()
    source_data = {'servers':{'server1': {'host': 'teve', 'port': 42}, 'server2': {'host': 'muha', 'port': 42}}}

    assert len(schema.schema) == 1
    assert schema(source_data) == source_data
    with raises(MultipleInvalid):
        assert schema({})
    with raises(MultipleInvalid):
        assert schema({'servers': 42})
    with raises(MultipleInvalid):
        assert schema({'servers': {12: {'host': '', 'port': 42}}})
    with raises(MultipleInvalid):
        assert schema({'servers': {'server': {'host': '', 'port': ''}}})

def test_dict_node_optional():
    tree = Tree()

    @tree.root()
    class Config():

        servers = tree.dict_node(str, ExampleServerConfig, {})

    schema = tree.build_schema()
    source_data = {'servers':{'server1': {'host': 'teve', 'port': 42}, 'server2': {'host': 'muha', 'port': 42}}}

    assert len(schema.schema) == 1
    assert schema(source_data) == source_data
    assert schema({}) == {'servers': {}}
    with raises(MultipleInvalid):
        assert schema({'servers': 42})

def test_dict_root():

    tree = Tree()

    @tree.dict_root(str, ExampleServerConfig)
    class Config():
        pass

    schema = tree.build_schema()
    source_data = {'server1': {'host': 'teve', 'port': 42}, 'server2': {'host': 'muha', 'port': 42}}

    assert len(schema.schema) == 1
    assert schema(source_data) == source_data
    with raises(MultipleInvalid):
        assert schema({12: {'host': '', 'port': 42}})
    with raises(MultipleInvalid):
        assert schema({'server': {'host': '', 'port': ''}})

def test_deep_dict_node():

    class ServerConfig(NodeBase):

        url = str

        def serialize(self):
            return self.__dict__

        class credentials(NodeBase):
            client_id = str
            secret = str

            def serialize(self):
                return self.__dict__

    tree = Tree()

    @tree.root()
    class Config():

        servers = tree.dict_node(str, ServerConfig)

    source_data = {'servers':{'server1': {'url': 'http://teve.hu', 'credentials': {'client_id': 'id1', 'secret': '42'}}}}
    source_data2 = deepcopy(source_data)
    source_data2['servers']['server1']['credentials']['client_id'] = 42
    source_data3 = deepcopy(source_data)
    del source_data3['servers']['server1']['credentials']['secret']

    schema = tree.build_schema()
    assert len(schema.schema) == 1
    assert schema(source_data) == source_data
    with raises(MultipleInvalid):
        assert schema(source_data2)
    with raises(MultipleInvalid):
        assert schema(source_data3)


def test_list_of_objects():

    class ServerConfig(NodeBase):

        url = str

        def serialize(self):
            return self.__dict__

        class credentials(NodeBase):
            client_id = str
            secret = str

            def serialize(self):
                return self.__dict__

    tree = Tree()

    @tree.root()
    class Config():

        servers = tree.list_node([ServerConfig])

    source_data = {'servers':[{'url': 'http://teve.hu', 'credentials': {'client_id': 'id1', 'secret': '42'}}]}
    source_data2 = deepcopy(source_data)
    source_data2['servers'][0]['credentials']['client_id'] = 42
    source_data3 = deepcopy(source_data)
    del source_data3['servers'][0]['credentials']['secret']

    schema = tree.build_schema()
    assert len(schema.schema) == 1
    assert schema(source_data) == source_data
    assert schema({'servers': []}) == {'servers': []}
    with raises(MultipleInvalid):
        assert schema(source_data2)
    with raises(MultipleInvalid):
        assert schema(source_data3)

def test_list_root():

    tree = Tree()

    @tree.list_root([int])
    class Config():
        pass

    schema = tree.build_schema()
    assert schema([1])

def test_list_root_without_class():

    tree = Tree()

    tree.set_root(tree.list_node([int]))

    schema = tree.build_schema()
    assert schema([1])
