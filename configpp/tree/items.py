
from abc import ABC, abstractmethod, abstractproperty
from voluptuous import UNDEFINED

class ItemBase():
    pass

class NodeBase(ABC, ItemBase):

    @abstractmethod
    def serialize(self):
        """Serialize the class

        Returns:
            any type of primitive types eg int, list, dict, str...
        """

class LeafBase(ABC, ItemBase):

    @classmethod
    def get_validator(cls):
        raise NotImplementedError()
