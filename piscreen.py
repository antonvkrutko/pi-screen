import time
from threading import Thread
from typing import Callable

import board
import digitalio
from PIL import ImageDraw, Image
from adafruit_rgb_display import st7789

from screen import Screen


class PiScreen(Screen):

    def __init__(self, refresh_time: float):
        self.refresh_time = refresh_time

        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = None
        baud_rate = 64000000

        self.display = st7789.ST7789(
            board.SPI(),
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=baud_rate,
            width=135,
            height=240,
            x_offset=53,
            y_offset=40,
        )

        backlight = digitalio.DigitalInOut(board.D22)
        backlight.switch_to_output()
        backlight.value = True

        height = self.display.width
        width = self.display.height

        self.image: Image = Image.new("RGBA", (width, height))

        draw = ImageDraw.Draw(self.image)
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0, 255))
        self.display.image(self.image, 90)

    def start_draw_cycle(self, draw_func: Callable[[Image or None], None]):
        Thread(target=self.draw_cycle_internal, args=[draw_func], daemon=True).start()

    def draw_on_screen(self, draw_func: Callable[[Image], None]):
        draw_func(self.image)
        self.display.image(self.image, 90)

    def draw_cycle_internal(self, draw_func: Callable[[Image or None], None]):
        while True:
            draw = ImageDraw.Draw(self.image)
            draw.rectangle((0, 0, self.image.width, self.image.height), outline=0, fill=(0, 0, 0))
            self.draw_on_screen(draw_func)
            time.sleep(self.refresh_time)
