from entities.ship import Ship
from libs.framework import Framework


# -------------------------------------------------------
#	game public interface
# -------------------------------------------------------

class Game:
    def __init__(self):
        self._ship = Ship()
        self._aircraft_list = []

    def init(self):
        self._ship.init()
        self._aircraft_list = self._ship.get_aircraft_list()

    def deinit(self):
        self._ship.deinit()
        for aircraft in self._aircraft_list:
            aircraft.deinit()

    def update(self, dt):
        self._ship.update(dt)
        for aircraft in self._aircraft_list:
            aircraft.update(dt)

    def keyPressed(self, key):
        self._ship.key_pressed(key)

    def keyReleased(self, key):
        self._ship.key_released(key)

    def mouseClicked(self, x, y, is_left_button):
        self._ship.mouse_clicked(x, y, is_left_button)


# -------------------------------------------------------
#	finally we can run our game!
# -------------------------------------------------------

if __name__ == u'__main__':
    Framework.run_game(Game())
