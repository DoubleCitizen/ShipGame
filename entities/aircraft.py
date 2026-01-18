# coding=utf-8
from entities.base_entity import BaseEntity
from libs.framework import Framework
from math_utils import Vector2
from params import Params, StateAI, Keys

import math
import time

class Aircraft(BaseEntity):

    def __init__(self):
        BaseEntity.__init__(self)
        self._input = {}
        self._is_alive = False
        self._is_parked = False
        self._is_on_ship = False
        self._state = StateAI.Aircraft.MOVING_TO_TARGET
        self._circle_radius = 0.0  # радиус круга вокруг цели
        self._circle_angle = 0.0  # текущий угол на окружности
        self._flight_time = 0.0
        self._ship_parent = None
        self._init_time = 0.0
        self._takeoff_distance_traveled = 0.0  # пройденное расстояние от корабля
        self._refuel_start_time = 0.0  # время, когда самолёт припарковался
        self._is_refueling = False  # флаг, что сейчас идёт заправка

    def init(self):
        BaseEntity.init(self)
        self._model = Framework.create_aircraft_model()
        self._position = Vector2()
        self._is_alive = False
        self._is_parked = False
        self._is_on_ship = False
        self._state = StateAI.Aircraft.MOVING_TO_TARGET
        self._angle = 0.0
        self._input = {
            Keys.AI.FORWARD: False,
            Keys.AI.BACKWARD: False,
            Keys.AI.LEFT: False,
            Keys.AI.RIGHT: False
        }
        self._circle_radius = Params.Aircraft.CIRCLE_RADIUS  # радиус круга вокруг цели
        self._circle_angle = 0.0  # текущий угол на окружности
        self._flight_time = Params.Aircraft.FLIGHT_TIME
        self._init_time = time.time()
        self._takeoff_distance_traveled = 0.0  # пройденное расстояние от корабля
        self._refuel_start_time = 0.0
        self._is_refueling = False

    def update(self, dt):
        if self._state == StateAI.Aircraft.TAKEOFF:
            self._start_takeoff(dt)
            return

        if not (self._is_alive and not self._is_parked):
            return

        # --- Управление ускорением ---
        target_linear_speed = 0.0
        if self._input.get(Keys.AI.FORWARD):
            target_linear_speed = Params.Aircraft.MAX_SPEED
        elif self._input.get(Keys.AI.BACKWARD):
            target_linear_speed = -Params.Aircraft.MAX_SPEED

        # Плавное ускорение/замедление
        if self._speed < target_linear_speed:
            self._speed += Params.Aircraft.ACCELERATION * dt
            if self._speed > target_linear_speed:
                self._speed = target_linear_speed
        elif self._speed > target_linear_speed:
            self._speed -= Params.Aircraft.ACCELERATION * dt
            if self._speed < target_linear_speed:
                self._speed = target_linear_speed

        # --- Управление поворотом ---
        angularSpeed = 0.0
        if self._input.get(Keys.AI.LEFT) and abs(self._speed) > 0.1:
            angularSpeed = Params.Aircraft.ANGULAR_SPEED
        elif self._input.get(Keys.AI.RIGHT) and abs(self._speed) > 0.1:
            angularSpeed = -Params.Aircraft.ANGULAR_SPEED

        self._angle += angularSpeed * dt
        direction = Vector2(math.cos(self._angle), math.sin(self._angle))
        displacement = direction * self._speed * dt
        self._position += displacement

        Framework.place_model(self._model, self._position.x, self._position.y, self._angle)

        # Обновляем ИИ-логику (она управляет _input)
        self.update_ai()

    def _to_park(self):
        self.deinit()
        self._is_parked = True
        self._is_refueling = True
        self._refuel_start_time = time.time()
        if self._ship_parent:
            self._ship_parent.add_aircraft(self)

    def update_ai(self):
        if time.time() - self._init_time > self._flight_time and self._state not in [StateAI.Aircraft.MOVING_TO_BEHIND_SHIP, StateAI.Aircraft.RETURN_TO_HOME]:
            self._state = StateAI.Aircraft.MOVING_TO_BEHIND_SHIP

        if self._state == StateAI.Aircraft.MOVING_TO_TARGET:
            self._move_to_target_logic()
        elif self._state == StateAI.Aircraft.CIRCLING:
            self._circle_around_target_logic()
        elif self._state == StateAI.Aircraft.MOVING_TO_BEHIND_SHIP:
            self._move_to_behind_ship()
        elif self._state == StateAI.Aircraft.RETURN_TO_HOME:
            self._return_to_home()
        elif self._state == StateAI.Aircraft.ALIGNING_TO_LAND:
            self._align_for_landing()

    def _align_for_landing(self):
        if not self._ship_parent:
            return
        ship_angle = self._ship_parent.get_angle()

        # Выравниваем угол самолёта по курсу корабля
        angle_diff = ship_angle - self._angle

        # Нормализация
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        self._set_controls_stop()
        self._input[Keys.AI.FORWARD] = True  # продолжаем движение

        if angle_diff > 0.1:
            self._input[Keys.AI.LEFT] = True
        elif angle_diff < -0.1:
            self._input[Keys.AI.RIGHT] = True
        else:
            # Угол выровнен — можно садиться
            self._state = StateAI.Aircraft.RETURN_TO_HOME

    def _set_controls_stop(self):
        self._input = {
            Keys.AI.FORWARD: False,
            Keys.AI.BACKWARD: False,
            Keys.AI.LEFT: False,
            Keys.AI.RIGHT: False
        }

    def _move_to_behind_ship(self):
        if not self._ship_parent:
            return

        ship_pos = self._ship_parent.get_position()
        ship_angle = self._ship_parent.get_angle()

        # Точка посадки — позади корабля
        landing_offset = 3.0
        landing_pos = ship_pos - Vector2(math.cos(ship_angle), math.sin(ship_angle)) * landing_offset

        # Вектор от самолёта к точке посадки
        to_landing = landing_pos - self._position
        distance_to_landing = to_landing.length()

        # Желаемый угол — направление К ТОЧКЕ ПОСАДКИ
        target_angle = math.atan2(to_landing.y, to_landing.x)
        angle_diff_to_target = target_angle - self._angle

        # Нормализация
        while angle_diff_to_target > math.pi:
            angle_diff_to_target -= 2 * math.pi
        while angle_diff_to_target < -math.pi:
            angle_diff_to_target += 2 * math.pi

        self._set_controls_stop()

        # === ФАЗА 1: ДАЛЕКО — АГРЕССИВНЫЙ ПОВОРОТ ===
        if distance_to_landing > 6.0:
            self._input[Keys.AI.FORWARD] = True
            if angle_diff_to_target > 0.0:
                self._input[Keys.AI.LEFT] = True
            else:
                self._input[Keys.AI.RIGHT] = True
            desired_speed = Params.Aircraft.MAX_SPEED * 1.0
            if self._speed > desired_speed + 0.1:
                self._input[Keys.AI.BACKWARD] = True
            elif self._speed < desired_speed - 0.1:
                self._input[Keys.AI.FORWARD] = True
        # === ФАЗА 2: БЛИЗКО — ЗАМЕДЛЯЕМСЯ И ГОТОВИМСЯ К ПОСАДКЕ ===
        else:
            # Замедляемся
            desired_speed = Params.Aircraft.MAX_SPEED * 0.3
            if self._speed > desired_speed + 0.1:
                self._input[Keys.AI.BACKWARD] = True
            elif self._speed < desired_speed - 0.1:
                self._input[Keys.AI.FORWARD] = True

            # Поворачиваемся к цели
            if angle_diff_to_target > 0.1:
                self._input[Keys.AI.LEFT] = True
            elif angle_diff_to_target < -0.1:
                self._input[Keys.AI.RIGHT] = True

            # === ПРОВЕРКА ПОСАДКИ ===
            close_to_landing = distance_to_landing < 4.0
            speed_ok = self._speed < (Params.Aircraft.MAX_SPEED * 0.4)

            # Выравнивание по курсу корабля
            course_diff = ship_angle - self._angle
            while course_diff > math.pi:
                course_diff -= 2 * math.pi
            while course_diff < -math.pi:
                course_diff += 2 * math.pi
            aligned_with_ship = abs(course_diff) < 0.1

            is_behind = self._is_behind(ship_pos, ship_angle)

            if not aligned_with_ship and close_to_landing and is_behind:
                self._state = StateAI.Aircraft.ALIGNING_TO_LAND

            # Если не выровнен — начинаем выравнивание (достаточно быть близко к точке)
            if aligned_with_ship and close_to_landing and is_behind:
                self._state = StateAI.Aircraft.RETURN_TO_HOME

    def _return_to_home(self):
        if not self._ship_parent:
            return

        ship_pos = self._ship_parent.get_position()
        ship_angle = self._ship_parent.get_angle()

        # Точка посадки — позади корабля
        landing_offset = 0.1
        landing_pos = ship_pos - Vector2(math.cos(ship_angle), math.sin(ship_angle)) * landing_offset

        # Вектор от самолёта к точке посадки
        to_landing = landing_pos - self._position
        distance_to_landing = to_landing.length()

        # Расстояние до корабля
        dist_to_ship = (self._position - ship_pos).length()

        # Желаемый угол — направление К ТОЧКЕ ПОСАДКИ
        target_angle = math.atan2(to_landing.y, to_landing.x)
        angle_diff_to_target = target_angle - self._angle

        # Нормализация
        while angle_diff_to_target > math.pi:
            angle_diff_to_target -= 2 * math.pi
        while angle_diff_to_target < -math.pi:
            angle_diff_to_target += 2 * math.pi

        self._set_controls_stop()

        desired_speed = Params.Aircraft.MAX_SPEED * 0.7
        if self._speed > desired_speed + 0.1:
            self._input[Keys.AI.BACKWARD] = True
        elif self._speed < desired_speed - 0.1:
            self._input[Keys.AI.FORWARD] = True

        # Поворачиваемся к цели
        if angle_diff_to_target > 0.1:
            self._input[Keys.AI.LEFT] = True
        elif angle_diff_to_target < -0.1:
            self._input[Keys.AI.RIGHT] = True

        # === ПРОВЕРКА ПОСАДКИ ===
        close_to_landing = distance_to_landing < 0.8

        is_behind = self._is_behind(ship_pos, ship_angle)

        # Посадка: близко к точке, выровнен, позади, медленно
        if is_behind and close_to_landing and dist_to_ship <= 0.3:
            self._to_park()
        elif dist_to_ship <= 0.5 and not is_behind:
            self._state = StateAI.Aircraft.MOVING_TO_BEHIND_SHIP

    def _is_behind(self, ship_pos, ship_angle):
        # Вектор от корабля к самолёту
        to_aircraft = self._position - ship_pos

        # Угол от корабля к самолёту
        to_aircraft_angle = math.atan2(to_aircraft.y, to_aircraft.x)

        # Угол от НОСА корабля до самолёта
        angle_from_nose = to_aircraft_angle - ship_angle

        # Нормализуем в [-π, π]
        while angle_from_nose > math.pi:
            angle_from_nose -= 2 * math.pi
        while angle_from_nose < -math.pi:
            angle_from_nose += 2 * math.pi

        # Угол от ХВОСТА корабля = угол от носа - π
        angle_from_tail = angle_from_nose - math.pi

        # Нормализуем снова
        while angle_from_tail > math.pi:
            angle_from_tail -= 2 * math.pi
        while angle_from_tail < -math.pi:
            angle_from_tail += 2 * math.pi

        # Проверяем: отклонение от хвоста < 30 градусов?
        max_deviation_rad = math.radians(30)  # 30° → радианы
        return abs(angle_from_tail) < max_deviation_rad

    def _move_to_target_logic(self):
        if not self._ship_parent or self._ship_parent.get_target_marker_position() is None:
            return

        target = self._ship_parent.get_target_marker_position()

        # Вектор от самолёта к цели
        to_target = target - self._position
        distance = to_target.length()

        if distance <= self._circle_radius:
            # ДОСТИГЛИ ЦЕЛИ → НАЧИНАЕМ КРУЖЕНИЕ ВОКРУГ НЕЁ
            self._state = StateAI.Aircraft.CIRCLING
            self._set_controls_stop()
            return

        # Угол направления к цели
        target_angle = math.atan2(to_target.y, to_target.x)
        angle_diff = target_angle - self._angle

        # Нормализация угла
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        self._set_controls_stop()
        self._input[Keys.AI.FORWARD] = True

        if angle_diff > 0.1:
            self._input[Keys.AI.LEFT] = True
        elif angle_diff < -0.1:
            self._input[Keys.AI.RIGHT] = True

    def _circle_around_target_logic(self):
        if not self._ship_parent or self._ship_parent.get_target_marker_position() is None:
            return

        target = self._ship_parent.get_target_marker_position()

        # Вектор от цели к самолёту
        to_target = self._position - target
        distance = to_target.length()

        if distance < 0.1:
            self._set_controls_stop()
            return

        # Нормализованный радиальный вектор (от цели к самолёту)
        radial_dir = to_target.normalized()

        # Желаемый радиус
        R = Params.Aircraft.CIRCLE_RADIUS

        # 1. Основное направление — по касательной (против часовой стрелки)
        tangent_dir = radial_dir.perpendicular_ccw()

        # 2. Добавляем радиальную коррекцию
        radial_error = distance - R  # >0 — слишком далеко, <0 — слишком близко

        # Коэффициент коррекции
        K_radial = 0.5

        # Корректируем направление:
        correction = radial_dir * (-K_radial * radial_error)

        # Итоговое желаемое направление
        desired_dir = tangent_dir + correction

        # Нормализуем
        desired_dir = desired_dir.normalized()

        # 3. Желаемый угол
        desired_angle = math.atan2(desired_dir.y, desired_dir.x)

        # 4. Разница углов
        angle_diff = desired_angle - self._angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        # 5. Управление
        self._set_controls_stop()
        self._input[Keys.AI.FORWARD] = True

        if angle_diff > 0.1:
            self._input[Keys.AI.LEFT] = True
        elif angle_diff < -0.1:
            self._input[Keys.AI.RIGHT] = True

    def _start_takeoff(self, dt):
        if not self._ship_parent:
            return

        ship_pos = self._ship_parent.get_position()
        ship_angle = self._ship_parent.get_angle()

        # Ускоряемся до максимальной скорости
        self._speed += Params.Aircraft.ACCELERATION * dt
        if self._speed > Params.Aircraft.MAX_SPEED:
            self._speed = Params.Aircraft.MAX_SPEED

        # Вместо этого — просто обновим позицию через общую логику:
        self._angle = ship_angle
        direction = Vector2(math.cos(self._angle), math.sin(self._angle))
        self._position = Vector2(ship_pos.x, ship_pos.y) + direction * self._takeoff_distance_traveled

        # Когда достигнем TAKEOFF_DISTANCE — выключаем _is_on_ship
        self._takeoff_distance_traveled += self._speed * dt
        if self._takeoff_distance_traveled >= Params.Aircraft.TAKEOFF_DISTANCE:
            self._is_on_ship = False
            self._state = StateAI.Aircraft.MOVING_TO_TARGET
            self._ship_parent.takeoff_plane_finish()

        Framework.place_model(self._model, self._position.x, self._position.y, self._angle)

    def spawn(self, x_spawn, y_spawn, angle_spawn, ship_parent):
        # --- ПРОВЕРКА ЗАПРАВКИ ---
        if self._is_parked and self._is_refueling:
            refuel_elapsed = time.time() - self._refuel_start_time
            if refuel_elapsed < Params.Aircraft.REFUEL_DURATION:
                # Самолёт ещё на заправке — нельзя поднимать
                return False  # <-- сигнализируем, что вызов не удался

        self.init()
        self._is_alive = True
        self._is_on_ship = True
        self._ship_parent = ship_parent
        self._state = StateAI.Aircraft.TAKEOFF
        self._takeoff_distance_traveled = 0.0
        self._position = Vector2(x_spawn, y_spawn)
        self._angle = angle_spawn
        Framework.place_model(self._model, x_spawn, y_spawn, angle_spawn)

        return True
