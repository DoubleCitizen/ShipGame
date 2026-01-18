# coding=utf-8
from entities.aircraft import Aircraft
from entities.base_entity import BaseEntity
from entities.target_marker import TargetMarker
from libs.framework import Framework

from math_utils import Vector2
from params import Params, Keys

import math


# -------------------------------------------------------
#	Simple ship logic
# -------------------------------------------------------

class Ship(BaseEntity):

    def __init__(self):
        BaseEntity.__init__(self)
        self._input = None
        self._aircraft_list = []
        self._aircraft_target = None
        self._is_takeoff_plane = False
        self._target_marker = None

    def init(self):
        BaseEntity.init(self)
        self._model = Framework.create_ship_model()
        self._position = Vector2()
        self._aircraft_list = [Aircraft() for _ in range(5)]
        self._input = {
            Keys.Player.FORWARD: False,
            Keys.Player.BACKWARD: False,
            Keys.Player.LEFT: False,
            Keys.Player.RIGHT: False
        }
        self._aircraft_target = Vector2()
        self._speed = 0.0
        self._is_takeoff_plane = False
        self._target_marker = TargetMarker()

    def deinit(self):
        BaseEntity.deinit(self)
        self._target_marker.deinit()

    def get_target_marker_position(self):
        return self._target_marker.get_position()

    def takeoff_plane_finish(self):
        self._is_takeoff_plane = False

    def get_aircraft_list(self):
        return list(self._aircraft_list)

    def add_aircraft(self, aircraft):
        self._aircraft_list.append(aircraft)

    def update(self, dt):
        linearSpeed = 0.0
        angularSpeed = 0.0

        if self._input[Keys.Player.FORWARD]:
            linearSpeed = Params.Ship.LINEAR_SPEED
        elif self._input[Keys.Player.BACKWARD]:
            linearSpeed = -Params.Ship.LINEAR_SPEED

        if self._input[Keys.Player.LEFT] and linearSpeed != 0.0:
            angularSpeed = Params.Ship.ANGULAR_SPEED
        elif self._input[Keys.Player.RIGHT] and linearSpeed != 0.0:
            angularSpeed = -Params.Ship.ANGULAR_SPEED

        self._angle += angularSpeed * dt

        # Вычисляем вектор скорости
        direction = Vector2(math.cos(self._angle), math.sin(self._angle))
        self._speed = direction * linearSpeed  # вектор скорости!

        # Обновляем позицию
        self._position += self._speed * dt
        Framework.place_model(self._model, self._position.x, self._position.y, self._angle)

    def key_pressed(self, key):
        self._input[key] = True

    def key_released(self, key):
        self._input[key] = False

    def mouse_clicked(self, x, y, is_left_button):
        if is_left_button:
            # Framework.place_goal_model(x, y)
            # self._aircraft_target = Vector2(x, y)
            self._target_marker.set_position(x, y)
        else:
            if not self._is_takeoff_plane:
                self.call_aircraft_target()

    def call_aircraft_target(self):
        if self._aircraft_list:
            aircraft = self._aircraft_list.pop(0)
            success = aircraft.spawn(self._position.x, self._position.y, self._angle, self)
            if success:
                self._is_takeoff_plane = True
            else:
                # Если заправка не закончена — вернём самолёт обратно
                self._aircraft_list.insert(0, aircraft)
