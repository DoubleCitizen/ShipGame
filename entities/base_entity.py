# coding=utf-8
from libs.framework import Framework
from math_utils import Vector2

import math


class BaseEntity:
    def __init__(self):
        self._model = None
        self._position = Vector2()
        self._angle = 0.0
        self._speed = 0.0
        self._is_initialized = False
        self._is_destroyed = False

    def init(self):
        """Вызывается один раз при создании."""
        assert not self._is_initialized, "Entity already initialized"
        self._is_initialized = True
        self._is_destroyed = False
        self._position = Vector2()
        self._angle = 0.0
        self._speed = 0.0

    def deinit(self):
        """Вызывается при уничтожении."""
        if not self._is_initialized or self._is_destroyed:
            return  # Защита от повторного вызова
        if self._model:
            Framework.destroy_model(self._model)
            self._model = None
        self._is_initialized = False
        self._is_destroyed = True

    def update_position(self, dt, linear_speed, angular_speed):
        """Общий метод для физики движения."""
        self._angle += angular_speed * dt
        direction = Vector2(math.cos(self._angle), math.sin(self._angle))
        displacement = direction * linear_speed * dt
        self._position += displacement
        Framework.place_model(self._model, self._position.x, self._position.y, self._angle)

    def get_position(self):
        return self._position

    def get_angle(self):
        return self._angle

    def get_speed(self):
        return self._speed

    def key_pressed(self, key):
        pass

    def key_released(self, key):
        pass