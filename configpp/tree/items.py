
from abc import ABC, abstractmethod, abstractproperty
from voluptuous import UNDEFINED

class ItemBase():
    pass

class NodeBase(ItemBase):

    def serialize(self):
        """Serialize the class

        Returns:
            any type of primitive types eg int, list, dict, str...
        """
        return self.__dict__

class LeafBase(ABC, ItemBase):

    @classmethod
    def get_validator(cls):
        raise NotImplementedError()
