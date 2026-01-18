# coding=utf-8
# -------------------------------------------------------
#	Basic Vector2 class
# -------------------------------------------------------
import math

class Vector2:

    def __init__(self, *args):
        if not args:
            self.x = self.y = 0.0
        elif len(args) == 1:
            self.x, self.y = args[0].x, args[0].y
        else:
            self.x, self.y = args

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, coef):
        return Vector2(self.x * coef, self.y * coef)

    def __rmul__(self, coef):
        return self.__mul__(coef)

    def length(self):
        """Возвращает длину вектора"""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        """Возвращает единичный вектор (направление)"""
        length = self.length()
        if length == 0:
            return Vector2(0, 0)  # защита от деления на 0
        return Vector2(self.x / length, self.y / length)

    def perpendicular_ccw(self):
        """Поворот вектора на 90° против часовой стрелки (для касательной)"""
        return Vector2(-self.y, self.x)