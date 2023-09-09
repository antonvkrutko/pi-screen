import time
from abc import abstractmethod
from threading import Thread
from typing import Callable

import PIL
from PIL.Image import Image


class Screen:

    @abstractmethod
    def draw_on_screen(self, draw_func: Callable[[Image or None], None]):
        pass

    @abstractmethod
    def start_draw_cycle(self, draw_func: Callable[[Image or None], None]):
        pass


class DummyScreen(Screen):

    def __init__(self, refresh_time: float, size: tuple[int, int]):
        self.refresh_time = refresh_time
        self.image = PIL.Image.new("RGBA", (size[0], size[1]))

    def start_draw_cycle(self, draw_func: Callable[[Image or None], None]):
        Thread(target=self.draw_cycle_internal, args=[draw_func], daemon=True).start()

    def draw_on_screen(self, draw_func: Callable[[Image or None], None]):
        draw_func(self.image)
        self.image.save("image.png")

    def draw_cycle_internal(self, draw_func: Callable[[Image or None], None]):
        while True:
            self.draw_on_screen(draw_func)
            time.sleep(self.refresh_time)
