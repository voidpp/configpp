import sys
import logging
import logging.handlers
from command_tree import CommandTree, Config
from voidpp_tools.colors import ColoredLoggerFormatter

from .core import Evolution, Chain
from .revision import REVISION_NUMBER_LENGTH


tree = CommandTree(Config(
    prepend_double_hyphen_prefix_if_arg_has_default = True,
    generate_simple_hyphen_name = {},
))


@tree.root()
@tree.argument(action = 'store_true', help = "log more stuffs")
class Root():

    def __init__(self, verbose = False):
        logger = logging.getLogger('configpp')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        handler.setFormatter(ColoredLoggerFormatter(verbose))
        logger.addHandler(handler)

    @tree.leaf(help = "Initialize a new scripts directory")
    @tree.argument(help = "location of scripts directory", nargs = '?')
    def init(self, folder = Evolution.DEFAULT_FOLDER):
        ev = Evolution()
        return 0 if ev.init(folder) else 1

    @tree.leaf(help = "Create a new revision file")
    @tree.argument(help = "Message")
    @tree.argument(help = "a new configpp uri in configpp://TODO format")
    def revision(self, message, uri: str = None):
        ev = Evolution()
        ev.load()
        return 0 if ev.revision(message, uri) else 1

    @tree.leaf(help = "Upgrade to a later version")
    @tree.argument(help = "Target revision", nargs = '?')
    def upgrade(self, target = 'head'):
        ev = Evolution()
        ev.load()
        ev.upgrade(target)
        return 0

    @tree.leaf(help = "List changeset scripts in chronological order")
    def history(self):
        ev = Evolution()
        ev.load()
        chain = ev.chain
        for id, rev in chain.links.items():
            print("{} -> {} : {}".format(rev.parent_id or ' ' * REVISION_NUMBER_LENGTH, rev.id, rev.message))
