# coding=utf-8
# -------------------------------------------------------
#	game parameters
# -------------------------------------------------------
from libs.framework import Framework


class Params:
    class Ship:
        LINEAR_SPEED = 0.5 # Линейная скорость
        ANGULAR_SPEED = 0.5 # Угловая скорость

    class Aircraft:
        MAX_SPEED = 2.0 # Максимальная скорость
        ANGULAR_SPEED = 2.5 # Угловая скорость
        CIRCLE_RADIUS = 1.5 # Радиус метки вокруг которой летают самолеты
        FLIGHT_TIME = 30.0 # Полетное время, сек
        ACCELERATION = 0.1 # Ускорение
        TAKEOFF_DISTANCE = 0.4 # Расстояние пройденное на палубе, после которого самолет считается взлетевшим
        REFUEL_DURATION = 5 # Время заправки, сек

class StateAI:
    class Aircraft:
        MOVING_TO_TARGET = "MOVING_TO_TARGET"
        CIRCLING = "CIRCLING"
        RETURN_TO_HOME = "RETURN_TO_HOME"
        ALIGNING_TO_LAND = "ALIGNING_TO_LAND"
        MOVING_TO_BEHIND_SHIP = "MOVING_TO_BEHIND_SHIP"
        TAKEOFF = "TAKEOFF"

        @staticmethod
        def is_moving(state):
            return state in [
                StateAI.Aircraft.MOVING_TO_TARGET,
                StateAI.Aircraft.MOVING_TO_BEHIND_SHIP
            ]

        @staticmethod
        def is_landing(state):
            return state in [
                StateAI.Aircraft.RETURN_TO_HOME,
                StateAI.Aircraft.ALIGNING_TO_LAND
            ]


class Keys:

    class Player:
        FORWARD = Framework.Keys.FORWARD
        BACKWARD = Framework.Keys.BACKWARD
        LEFT = Framework.Keys.LEFT
        RIGHT = Framework.Keys.RIGHT

    class AI:
        FORWARD = "forward"
        BACKWARD = "backward"
        LEFT = "left"
        RIGHT = "right"
