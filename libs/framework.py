# coding=utf-8
try:
    import framework32 as framework
except:
    import framework64 as framework

class Framework:
    @staticmethod
    def create_aircraft_model():
        """Создаёт новую модель самолёта и возвращает ее"""
        return framework.createAircraftModel()

    @staticmethod
    def create_ship_model():
        """Создаёт новую модель корабля и возвращает ее"""
        return framework.createShipModel()

    @staticmethod
    def destroy_model(model):
        """Удаляет модель, созданную любой из создающих функций"""
        framework.destroyModel(model)

    @staticmethod
    def place_model(model, x, y, angle):
        """Располагает модель в мире в указанных координатах и повёрнутой под нужным углом"""
        framework.placeModel(model, x, y, angle)

    @staticmethod
    def place_goal_model(x, y):
        """Располагает метку для самолетов"""
        framework.placeGoalModel(x, y)

    @staticmethod
    def run_game(game):
        """Запускает игру"""
        framework.runGame(game)

    class Keys:
        FORWARD = framework.Keys.FORWARD
        BACKWARD = framework.Keys.BACKWARD
        LEFT = framework.Keys.LEFT
        RIGHT = framework.Keys.RIGHT