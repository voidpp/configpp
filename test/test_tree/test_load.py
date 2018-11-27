
from pytest import mark, raises
from configpp.tree import Tree, NodeBase, LeafFactory
from typing import List, Dict
from voluptuous import MultipleInvalid

def test_simple_param_default():

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = 42

    cfg = tree.load({})

    assert cfg.param_simpe_1 == 42

def test_simple_param_required():

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = int

    cfg = tree.load({'param_simpe_1': 42})

    assert cfg.param_simpe_1 == 42

def test_deep_load():

    tree = Tree()

    @tree.root()
    class Config():

        @tree.node()
        class oidc():
            url = str

            @tree.node()
            class credentials():
                client_id = str
                key = str

    source_data = {'oidc': {'url': 'teve', 'credentials': {'client_id': 'muha', 'key': 'da_key'}}}

    cfg = tree.load(source_data)
    assert cfg.oidc.url == 'teve'
    assert cfg.oidc.credentials.client_id == 'muha'
    assert cfg.oidc.credentials.key == 'da_key'

def test_dict_node_load():

    class ServerConfig(NodeBase):

        host = str
        port = int

        def serialize(self):
            return self.__dict__

    tree = Tree()

    @tree.root()
    class Config():

        servers = tree.dict_node(str, ServerConfig)

    source_data = {'servers':{'server1': {'host': 'teve', 'port': 42}, 'server2': {'host': 'muha', 'port': 422}}}

    cfg = tree.load(source_data)

    assert cfg.servers['server1'].host == 'teve'
    assert cfg.servers['server1'].port == 42
    assert cfg.servers['server2'].host == 'muha'
    assert cfg.servers['server2'].port == 422


def test_deep_dict_node_load():

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

    cfg = tree.load(source_data)

    assert cfg.servers['server1'].url == 'http://teve.hu'
    assert cfg.servers['server1'].credentials.client_id == 'id1'
    assert cfg.servers['server1'].credentials.secret == '42'

def test_list_node_load_one_type():

    class ServerConfig(NodeBase):

        host = str
        port = int

        def serialize(self):
            return self.__dict__

    tree = Tree()

    @tree.root()
    class Config():

        servers = tree.list_node([ServerConfig])

    source_data = {'servers':[{'host': 'teve', 'port': 42}, {'host': 'muha', 'port': 422}]}

    cfg = tree.load(source_data)

    assert cfg.servers[0].host == 'teve'
    assert cfg.servers[0].port == 42
    assert cfg.servers[1].host == 'muha'
    assert cfg.servers[1].port == 422


def test_list_node_load_two_types():

    class ServerConfig(NodeBase):

        host = str
        port = int

        def serialize(self):
            return self.__dict__

    tree = Tree()

    @tree.root()
    class Config():

        servers = tree.list_node([ServerConfig, int])

    source_data = {'servers':[{'host': 'teve', 'port': 42}, 21]}

    cfg = tree.load(source_data)

    assert cfg.servers[0].host == 'teve'
    assert cfg.servers[0].port == 42
    assert cfg.servers[1] == 21

def test_pure_leaf_factory():

    tree = Tree()

    @tree.root()
    class Config():

        var1 = LeafFactory(int, 42)

    assert tree.load({}).var1 == 42

    with raises(MultipleInvalid):
        assert tree.load({'var1': 'teve'})
