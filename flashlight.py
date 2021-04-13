import time

import board
import color
import neopixel
import touchio


CLICK_MAX_LENGTH_MSEC = 200
CLICK_TIMEOUT_MSEC = 200

NUM_PIXELS = 4

COLORS = [
    color.WHITE,
    color.RED,
    color.ORANGE,
    color.YELLOW,
    color.GREEN,
    color.BLUE,
    color.PURPLE
]

INTENSITIES = [1.0, 0.66, 0.33, 0.0]


def time_msec():
    return int(time.monotonic() * 1000)


class Button:

    def __init__(self, hw_button, callback=None):
        self.hw_button = hw_button
        self.callback = callback

        self.last_state = hw_button.value
        self.last_edge_time = 0
        self.num_clicks = 0

    def update(self):
        current_state = self.hw_button.value
        current_time = time_msec()

        if current_state != self.last_state:
            if (current_state is False and
                    current_time - self.last_edge_time < CLICK_MAX_LENGTH_MSEC):
                self.num_clicks += 1

            self.last_edge_time = current_time
        else:
            if (current_state is False and
                    current_time - self.last_edge_time > CLICK_TIMEOUT_MSEC):
                if self.num_clicks > 0 and self.callback is not None:
                    self.callback(self, self.num_clicks)

                self.num_clicks = 0

        self.last_state = current_state


class Task():
    def __init__(self, interval):
        self.interval = interval
        self.last_time = 0

    def update(self):
        now = time_msec()
        if now - self.last_time > self.interval:
            self.last_time = now
            self._run()

    def _run(self):
        pass # override in subclass


class SolidColorLED(Task):

    def __init__(self, pixels, led_color, interval):
        super().__init__(interval)
        self.pixels = pixels
        self.led_color = led_color
        self.intensity = 1.0

    def _run(self):
        self.pixels.fill(color.calculate_intensity(self.led_color, self.intensity))
        self.pixels.show()


class RainbowLED(Task):

    def __init__(self, pixels, interval):
        super().__init__(interval)
        self.pixels = pixels
        self.j = 0
        self.intensity = 1.0

    def _run(self):
        for i in range(NUM_PIXELS):
            index = (i * 256 // NUM_PIXELS) + self.j % 256
            self.pixels[i] = color.calculate_intensity(
                color.colorwheel(index & 255), self.intensity)

        self.pixels.show()
        self.j += 1


class MCP:

    def __init__(self, button1, button2, rainbow_led, solid_led):

        self.button1 = button1
        self.button2 = button2
        self.rainbow_led = rainbow_led
        self.solid_led = solid_led
        self.button1.callback = self.click
        self.button2.callback = self.click
        self.color_index = 0
        self.intensity_index = 0
        self.active_led_task = self.solid_led

    def run(self):
        while True:
            self.button1.update()
            self.button2.update()
            self.active_led_task.update()

    def click(self, button, _):
        if button == self.button1:
            self.intensity_index = (self.intensity_index + 1) % len(INTENSITIES)
            self.solid_led.intensity = INTENSITIES[self.intensity_index]
            self.rainbow_led.intensity = INTENSITIES[self.intensity_index]
        else: # button2
            if INTENSITIES[self.intensity_index] <= 0.1:
                return

            self.color_index += 1
            if self.color_index == len(COLORS):
                self.active_led_task = self.rainbow_led
                self.color_index = -1
            else:
                self.active_led_task = self.solid_led
                self.solid_led.led_color = COLORS[self.color_index]


def main():
    touch1 = touchio.TouchIn(board.TOUCH1)
    touch2 = touchio.TouchIn(board.TOUCH2)
    button1 = Button(touch1)
    button2 = Button(touch2)

    pixels = neopixel.NeoPixel(
        board.NEOPIXEL, NUM_PIXELS, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

    rainbow = RainbowLED(pixels, 10)
    solid = SolidColorLED(pixels, color.WHITE, 100)

    mcp = MCP(button1, button2, rainbow, solid)
    mcp.run()


main()
