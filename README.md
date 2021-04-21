# Neo Trinkey

Scripts of varying utility for the [Adafruit Neo Trinkey](https://www.adafruit.com/product/4870) ATSAMD21 microcontroller board.

![4870-02](https://user-images.githubusercontent.com/251168/114488192-cc193a00-9bc5-11eb-909c-7133a67af6b9.jpg)

Copy scripts in the root level as 'code.py' on the device.

flashlight.py
- T1: Change LED color or show an animated rainbow.
- T2: Change LED brightness or turn off.

serial_control.py
 - Control LEDs via the serial interface. See comments in the script for details.
 - Use the serial_control_host.py script for a command line interface to the Neo trinkey LEDs

volume_control.py
 - T1: Tap once to increase volume. Tap twice to play/pause.
 - T2: Tap once to decrease volume. Tap twice to mute/unmute.

stackoverflow_helper.py
 - T1: Tap once to copy. Tap twice to cut.
 - T2: Tap once to paste. Tap twice to swich between Mac/Windows

