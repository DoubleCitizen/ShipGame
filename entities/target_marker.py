from libs.framework import Framework
from math_utils import Vector2

class TargetMarker:
    def __init__(self):
        self._position = Vector2()

    def deinit(self):
        self.set_position(0, 0)

    def get_position(self):
        return self._position

    def set_position(self, x, y):
        self._position.x = x
        self._position.y = y
        Framework.place_goal_model(x, y)