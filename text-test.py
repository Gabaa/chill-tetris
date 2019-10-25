import pyglet


class EndScreen:
    enter_name_label: pyglet.text.Label
    name_label: pyglet.text.Label

    def __init__(self):
        self.enter_name_label = pyglet.text.Label('ENTER YOUR NAME',
                                                  x=window.width // 2,
                                                  y=window.height * 0.7,
                                                  anchor_x='center',
                                                  anchor_y='center')
        self.name_label = pyglet.text.Label('',
                                            x=window.width // 2,
                                            y=window.height * 0.5,
                                            anchor_x='center', anchor_y='center',
                                            font_size=20)

    def draw(self):
        self.enter_name_label.draw()
        self.name_label.draw()

    def on_key_press(self, key, mod):
        if key == pyglet.window.key.BACKSPACE:
            self.name_label.text = self.name_label.text[:-1]
        elif key == pyglet.window.key.ENTER:
            pyglet.app.exit()

    def on_text(self, text):
        if text.lower() in 'abcdefghijklmnopqrstuvwxyzæøå':
            self.name_label.text += text
            print(self.name_label.text)


window = pyglet.window.Window()
endscreen = EndScreen()


@window.event
def on_draw():
    window.clear()
    endscreen.draw()

@window.event
def on_key_press(key, mod):
    endscreen.on_key_press(key, mod)


@window.event
def on_text(text):
    endscreen.on_text(text)


pyglet.app.run()
