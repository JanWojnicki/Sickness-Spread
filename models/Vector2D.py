# models/Vector2D.py
from interfaces.IVector import IVector
import math

class Vector2D(IVector):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #Zwraca komponenty wektora jako listę
    def getComponents(self):
        return [self.x, self.y]

    #Oblicza iloczyn skalarny z innym wektorem 2D
    def cdot(self, param):
        components = param.getComponents()
        x2, y2 = components[0], components[1]
        return self.x * x2 + self.y * y2
    
    #Długość wektora
    def abs(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    #Dystans do innego wektora 2D
    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx ** 2 + dy ** 2)
