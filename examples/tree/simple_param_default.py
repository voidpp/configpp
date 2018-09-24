from configpp.tree import Tree

tree = Tree()

@tree.root()
class Config():

    param_simple_1 = 42

cfg = tree.load({})

print(cfg.param_simple_1)
