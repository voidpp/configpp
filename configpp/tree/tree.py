import logging
from voluptuous import Schema, UNDEFINED

from configpp.tree.settings import Settings
from configpp.tree.exceptions import ConfigTreeBuilderException
from configpp.tree.item_factory import AttrNodeFactory, LeafFactory, DictNodeFactory, ListNodeFactory, LeafFactoryRegistry

from configpp.tree.custom_item_factories import DateTimeLeafFactory, datetime, EnumLeafFactory, Enum

logger = logging.getLogger(__name__)

class Tree():

    def __init__(self, settings: Settings = None):
        self._settings = settings or Settings()
        self._root = None  # type: AttrNodeFactory
        self._extra_items = {}
        self._leaf_factory_registry = {
            datetime: DateTimeLeafFactory,
            Enum: EnumLeafFactory,
        }  # type: LeafFactoryRegistry

    def register_leaf_factory(self, type_: type, factory: LeafFactory):
        self._leaf_factory_registry[type_] = factory

    def build_schema(self) -> Schema:
        if self._root is None:
            raise ConfigTreeBuilderException("There is no root!")
        return self._root.create_schema()

    def load(self, raw_data: dict):
        schema = self.build_schema()
        data = schema(raw_data)
        return self._root.process_value(data)

    def dump(self, data) -> dict:
        return self._root.dump(data)

    def root(self, excluded_attributes: list = None):
        if self._root is not None:
            logger.warning("Root node has been set already to: %s", self._root)
        def decor(cls):
            self._root = AttrNodeFactory(cls, self._settings, self._leaf_factory_registry, excluded_attributes,
                                         external_item_registry = self._extra_items)
            return cls
        return decor

    def dict_root(self, key_type, value_type, default = UNDEFINED):
        if self._root is not None:
            logger.warning("Root node has been set already to: %s", self._root)
        def decor(cls):
            self._root = DictNodeFactory(key_type, value_type, self._settings, self._leaf_factory_registry, default)
            return cls
        return decor

    def list_root(self, value_types, default = UNDEFINED):
        if self._root is not None:
            logger.warning("Root node has been set already to: %s", self._root)
        def decor(cls):
            self._root = ListNodeFactory(value_types, self._settings, self._leaf_factory_registry, default)
            return cls
        return decor

    def node(self, excluded_attributes: list = None, default = UNDEFINED):
        def wrapper(cls: type):
            node = AttrNodeFactory(cls, self._settings, self._leaf_factory_registry, excluded_attributes, default,
                                   external_item_registry = self._extra_items)
            cls._configpp_tree_item = node
            return cls
        return wrapper

    def dict_node(self, key_type, value_type, default = UNDEFINED):
        return DictNodeFactory(key_type, value_type, self._settings, self._leaf_factory_registry, default)

    def list_node(self, value_types: list, default = UNDEFINED):
        """TODO"""
        return ListNodeFactory(value_types, self._settings, self._leaf_factory_registry, default)

    def leaf(self, validator = None, default = UNDEFINED):
        return LeafFactory(validator, default)
