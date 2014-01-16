__author__ = 'justinarmstrong'

class Mushroom(pg.sprite.Sprite):

    def __init__(self, x, y):
        super(Mushroom, self).__init__()
        self.x = x
        self.y = y
        self.state = c.REVEAL


    def update(self):
        self.handle_state()

    def handle_state(self):
        if self.state == c.REVEAL:
            self.revealing()

    def revealing(self):
        pass
