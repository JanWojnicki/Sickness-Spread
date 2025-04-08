# interfaces/IVector.py
from abc import ABC, abstractmethod

class IVector(ABC):
    @abstractmethod
    def getComponents(self):
        pass

    @abstractmethod
    def cdot(self, param):
        pass
