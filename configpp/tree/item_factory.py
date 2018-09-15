import inspect
from abc import ABC, abstractmethod
from typing import Dict
from functools import partial
from voluptuous import Required, Optional, UNDEFINED, Schema, MultipleInvalid

from configpp.tree.items import NodeBase
from configpp.tree.exceptions import ConfigTreeBuilderException, ConfigTreeDumpException
from configpp.tree.settings import Settings

from typing import get_type_hints, GenericMeta

from re import finditer

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

class ItemFactoryBase(ABC):

    def __init__(self, default):
        self._default = default

    @property
    def default(self):
        return self._default

    @abstractmethod
    def create_schema(self):
        pass

    @abstractmethod
    def process_value(self, value, parent_instance = None):
        pass

    @abstractmethod
    def dump(self, value):
        pass

    def get_key_validator(self, key):
        cls = Required if self._default == UNDEFINED else Optional
        return cls(key, default = self._default)

class LeafFactory(ItemFactoryBase):

    def __init__(self, validator = None, default = UNDEFINED):
        super().__init__(default)
        self._validator = validator

    def create_schema(self):
        return self._validator

    def dump(self, value):
        return value

    def process_value(self, value, parent_instance = None):
        return value

    def __repr__(self):
        return "<LeafFactory default: {}, validator: {}".format(self._default, self._validator)

LeafFactoryRegistry = Dict[type, LeafFactory]

class NodeFactory(ItemFactoryBase):
    def __init__(self, settings: Settings, leaf_factory_registry: LeafFactoryRegistry, default = UNDEFINED):
        super().__init__(default)
        self._settings = settings
        self._leaf_factory_registry = leaf_factory_registry

    def get_leaf_factory(self, type_) -> LeafFactory:
        # search for exact match
        factory = self._leaf_factory_registry.get(type_)
        if factory is not None:
            return factory

        # search by parent
        for ftype, factory in self._leaf_factory_registry.items():
            if issubclass(type_, ftype):
                return factory

        return LeafFactory

    def create_item(self, attr) -> ItemFactoryBase:
        if inspect.isfunction(attr):
            return None

        if isinstance(attr, ItemFactoryBase):
            return attr

        elif isinstance(attr, NodeBase):
            return AttrNodeFactory(type(attr), self._settings, self._leaf_factory_registry, default = attr.serialize())

        elif isinstance(attr, list):
            return ListNodeFactory(attr, self._settings, self._leaf_factory_registry)

        else:
            if inspect.isclass(attr):
                if NodeBase in inspect.getmro(attr):
                    return AttrNodeFactory(attr, self._settings, self._leaf_factory_registry)
                else:
                    return self.get_leaf_factory(attr)(attr)
            else:
                return self.get_leaf_factory(type(attr))(type(attr), attr)

class AttrNodeFactory(NodeFactory):
    def __init__(self, cls: type, settings: Settings, leaf_factory_registry: LeafFactoryRegistry, excluded_attributes: list = None,
                 default = UNDEFINED, external_item_registry: Dict[int, ItemFactoryBase] = None):
        super().__init__(settings, leaf_factory_registry, default)
        self._cls = cls
        self._excluded_attributes = excluded_attributes or []
        self._items = {}  # type: Dict[str, ItemFactoryBase]
        self._external_item_registry = external_item_registry or {}
        self._attribute_map = {}  # type: Dict[str, str]

    @property
    def cls(self):
        return self._cls

    def dump(self, instance):
        res = {}
        for name, item in self._items.items():
            res[self._attribute_map[name]] = item.dump(getattr(instance, name))
        return res

    def process_value(self, value, parent_instance = None):
        instance = self._cls()

        if self._settings.dump_method_name_in_node_classes:
            setattr(instance, self._settings.dump_method_name_in_node_classes, partial(self.dump, instance))

        for name, item in self._items.items():
            val = item.process_value(value[self._attribute_map[name]], instance)
            setattr(instance, name, val)
        return instance

    def _iter_member(self, name: str, attr, result: dict):
        if name in self._excluded_attributes:
            return

        if self._settings.member_iteration_filter_pattern.search(name):
            return

        attr_id = id(attr)

        if hasattr(attr, '_configpp_tree_item'):
            item = getattr(attr, '_configpp_tree_item')
        elif attr_id in self._external_item_registry:
            item = self._external_item_registry[attr_id]
        elif isinstance(attr, GenericMeta):
            if issubclass(attr, list):
                item = ListNodeFactory(attr.__args__, self._settings, self._leaf_factory_registry)
            elif issubclass(attr, dict):
                item = DictNodeFactory(*attr.__args__, self._settings, self._leaf_factory_registry)
            else:
                # TODO print some log error?
                return
        else:
            item = self.create_item(attr)

        if item is None:
            return

        data_key_name = name
        if self._settings.convert_underscores_to_hypens:
            data_key_name = name.replace('_', '-')

        if self._settings.convert_camel_case_to_hypens:
            data_key_name = '-'.join(camel_case_split(name)).lower()

        self._attribute_map[name] = data_key_name
        self._items[name] = item

        item_schema = item.create_schema()

        result[item.get_key_validator(data_key_name)] = item_schema

    def create_schema(self):
        schema_dict = {}
        for name, attr in inspect.getmembers(self._cls):
            self._iter_member(name, attr, schema_dict)

            # without this the self.process_value will not able to set the value for this attribute
            if isinstance(attr, property):
                delattr(self._cls, name)

        for name, hint in get_type_hints(self._cls).items():
            if name not in self._items:
                self._iter_member(name, hint, schema_dict)

        schema = Schema(schema_dict)

        for item in self._items.values():
            if item.default == UNDEFINED:
                break
        else:
            self._default = schema({})

        return schema

class DictNodeFactory(NodeFactory):
    def __init__(self, key_type: type, value_type: type, settings: Settings, leaf_factory_registry: LeafFactoryRegistry, default = UNDEFINED):
        super().__init__(settings, leaf_factory_registry, default = default)
        self._key_type = key_type
        self._value_type = value_type
        self._item = None # type: ItemFactoryBase

    def create_schema(self):
        self._item = self.create_item(self._value_type)
        return Schema({self._key_type: self._item.create_schema()})

    def process_value(self, value: dict, parent_instance = None):
        res = {}
        for key, val in value.items():
            res[key] = self._item.process_value(val)
        return res

    def dump(self, instance: dict):
        res = {}
        for key, value in instance.items():
            res[key] = self._item.dump(instance[key])
        return res

class ListNodeFactory(NodeFactory):
    def __init__(self, value_types: list, settings: Settings, leaf_factory_registry: LeafFactoryRegistry, default = UNDEFINED):
        super().__init__(settings, leaf_factory_registry, default = default)
        self._value_types = value_types
        self._schemas = []
        self._items = []

    def create_schema(self):
        for type_ in self._value_types:
            if isinstance(type_, type):
                break
        else:
            self._default = self._value_types

        self._items = [self.create_item(type_) for type_ in self._value_types]
        self._schemas = [item.create_schema() for item in self._items]
        return self._schemas

    def process_value(self, value: list, parent_instance = None):
        res = []
        for val in value:
            # searching the matching schema and ItemFactory
            for idx, schema in enumerate(self._schemas):
                try:
                    schema(val)
                    res.append(self._items[idx].process_value(val))
                    break
                except MultipleInvalid:
                    continue
            else:
                raise ConfigTreeBuilderException("Matching schema not found for value: '{}'".format(val))
        return res

    def dump(self, instance: []):
        if len(self._items) > 1:
            raise ConfigTreeDumpException("cannot dump a list with multiple types yet")
        res = []
        for value in instance:
            res.append(self._items[0].dump(value))
        return res
