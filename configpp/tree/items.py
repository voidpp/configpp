
from abc import ABC, abstractmethod

class ItemBase():
    pass

class NodeBase(ABC, ItemBase):

    @abstractmethod
    def serialize(self):
        """Serialize the class

        Returns:
            any type of primitive types eg int, list, dict, str...
        """
