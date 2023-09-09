from abc import abstractmethod
from typing import cast

import PIL
from PIL import ImageFont, ImageColor
from PIL.Image import Image
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont

from meeting_info import MeetingInfo
from screen import Screen


class Output:

    @abstractmethod
    def set_meeting_info(self, info: MeetingInfo):
        pass

    @abstractmethod
    def set_meeting_free(self, message: str):
        pass


class ScreenOutput(Output):

    def __init__(self, screen: Screen):
        self.screen = screen

        self.meeting_info_time_info_offset = 0
        self.meeting_info_title_offset = 0
        self.message_offset = 0

        self.meeting_info: MeetingInfo or None = None
        self.message: str or None = None
        try:
            self.font: FreeTypeFont = ImageFont.truetype("DejaVuSans.ttf", 24)
        except Exception as e:
            print("Can't load font:", e)
        self.screen.start_draw_cycle(self.draw_internal)

    def set_meeting_info(self, info: MeetingInfo):
        self.meeting_info = info
        self.meeting_info_time_info_offset = 0
        self.meeting_info_title_offset = 0

    def set_meeting_free(self, message: str):
        self.meeting_info = None
        self.message = message
        self.message_offset = 0

    def draw_internal(self, image: Image):
        if self.meeting_info is None:
            self.draw_free_internal(image)
        else:
            self.draw_meeting_internal(image)

    def draw_meeting_internal(self, image: Image):
        meeting_info = cast(MeetingInfo, self.meeting_info)

        if meeting_info.is_free:
            background_color = ImageColor.getrgb("Gold")
        else:
            background_color = ImageColor.getrgb("Crimson")
        self.draw_background_internal(
            image=image,
            color=background_color
        )

        draw = ImageDraw(image)
        draw.text((0, 0), self.meeting_info.title, font=self.font)

    def draw_free_internal(self, image: Image):
        self.draw_background_internal(
            image=image,
            color=ImageColor.getrgb("ForestGreen")
        )
        if self.message is not None:
            font = self.font.font_variant(size=36)
            (l, t, r, b) = font.getbbox(self.message)
            padding = 10
            image_for_text = PIL.Image.new(
                mode="RGBA",
                size=(image.width - padding * 2, b),
            )
            text_draw = ImageDraw(image_for_text)
            text_draw.text((self.message_offset, 0), text=self.message, font=font, anchor="lt")

            if r - l > image_for_text.width:
                self.message_offset -= 3
                if abs(self.message_offset) >= r - l:
                    self.message_offset = image_for_text.width

            image.paste(
                im=image_for_text,
                box=(padding, round(image.height / 2 - (b - t) / 2)),
                mask=image_for_text
            )

    def draw_background_internal(self, image: Image, color: ImageColor):
        draw = ImageDraw(image)
        draw.rounded_rectangle(
            xy=(0, 0, image.width, image.height),
            radius=20,
            fill=color,
        )
