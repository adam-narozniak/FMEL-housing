from pynput import mouse

ith_click = 0
clicks_coordinates = []


def on_move(x, y):
    print(f"On move: x,y = {x}, {y}")

def on_click(x, y, button, pressed):
    print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    global ith_click
    if not pressed:
        ith_click += 1
        clicks_coordinates.append({"x": x, "y": y})
    if ith_click == 2:
        # Stop listener
        return False





def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))
