# Use Neo Trinkey (https://www.adafruit.com/product/4870) to copy/paste.
# Touch 1 - Tap once to copy. Tap twice to cut.
# Touch 2 - Tap once to paste. Tap twice to swich between Mac/Windows
#
# Copy stackoverlow_helper.py to the Neo Trinkey as code.py

import time

import board
import color
import neopixel
import touchio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

CLICK_MAX_LENGTH_MSEC = 200
CLICK_TIMEOUT_MSEC = 200

NUM_PIXELS = 4

INTENSITY = 0.1
BLINK_DURATION = 50


def time_msec():
    return int(time.monotonic() * 1000)


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


class Button(Task):

    def __init__(self, hw_button, run_interval, callback=None):
        super().__init__(run_interval)
        self.hw_button = hw_button
        self.callback = callback

        self.last_state = hw_button.value
        self.last_edge_time = 0
        self.num_clicks = 0

    def _run(self):
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


class LEDBlink(Task):

    def __init__(self, pixels, intensity, run_interval):
        super().__init__(run_interval)
        self.pixels = pixels
        self.intensity = intensity
        self.stop_time = 0

    def _run(self):
        if time_msec() >= self.stop_time:
            self.pixels.fill(color.BLACK)
            self.pixels.show()

    def blink(self, clr, duration):
        self.pixels.fill(color.calculate_intensity(clr, self.intensity))
        self.pixels.show()
        self.stop_time = time_msec() + duration


class MCP:

    def __init__(self, button1, button2, keyboard, led):
        self.button1 = button1
        self.button2 = button2
        self.keyboard = keyboard
        self.led = led
        self.modifier_key = Keycode.COMMAND

    def click(self, button, num_clicks):

        if button == self.button1 and num_clicks == 1:
            self.keyboard.send(self.modifier_key, Keycode.C)
            self.led.blink(color.YELLOW, BLINK_DURATION)

        elif button == self.button1 and num_clicks == 2:
            self.keyboard.send(self.modifier_key, Keycode.X)
            self.led.blink(color.RED, BLINK_DURATION)

        elif button == self.button2 and num_clicks == 1:
            self.keyboard.send(self.modifier_key, Keycode.V)
            self.led.blink(color.GREEN, BLINK_DURATION)

        elif button == self.button2 and num_clicks == 2:
            if self.modifier_key == Keycode.COMMAND:
                self.modifier_key = Keycode.CONTROL
            else:
                self.modifier_key = Keycode.COMMAND

            self.led.blink(color.BLUE, BLINK_DURATION)


def main():

    touch1 = touchio.TouchIn(board.TOUCH1)
    touch2 = touchio.TouchIn(board.TOUCH2)
    button1 = Button(touch1, 10)
    button2 = Button(touch2, 10)

    keyboard = Keyboard(usb_hid.devices)

    pixels = neopixel.NeoPixel(
        board.NEOPIXEL, NUM_PIXELS, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

    led = LEDBlink(pixels, INTENSITY, 10)

    mcp = MCP(button1, button2, keyboard, led)
    button1.callback = mcp.click
    button2.callback = mcp.click

    tasks = [button1, button2, led]
    while True:
        for task in tasks:
            task.update()


if __name__ == '__main__':
    main()
