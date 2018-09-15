
from configpp.tree import Tree, NodeBase
from typing import List, Dict

def test_dump_simple_param():

    tree = Tree()

    @tree.root()
    class Config():

        param_simpe_1 = 42

    cfg = tree.load({})

    cfg.param_simpe_1 = 84

    data = tree.dump(cfg)

    assert data['param_simpe_1'] == 84

def test_deep_dump():

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

    cfg.oidc.credentials.client_id = 'teve'

    data = tree.dump(cfg)

    assert data['oidc']['credentials']['client_id'] == 'teve'

def test_dict_node_dump():

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

    cfg.servers['server1'].port = 5042

    data = tree.dump(cfg)

    assert data['servers']['server1']['port'] == 5042

def test_list_node_dump_one_type():

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

    cfg.servers[0].port = 84

    data = tree.dump(cfg)

    assert data['servers'][0]['port'] == 84
