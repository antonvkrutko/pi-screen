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
            background_color = ImageColor.getrgb("Orange")
        else:
            background_color = ImageColor.getrgb("Crimson")
        self.draw_background_internal(
            image=image,
            color=background_color
        )

        y_position = 0
        # Drawing meeting title
        self.meeting_info_title_offset = self.draw_text_internal(
            image=image,
            xy=(0, y_position),
            font=self.font.font_variant(size=30),
            padding=(10, 10),
            text=meeting_info.title,
            offset=self.meeting_info_title_offset
        )
        y_position = self.font.getbbox(text=meeting_info.title)[3]

        # Drawing time message
        y_position += 10
        self.meeting_info_time_info_offset = self.draw_text_internal(
            image=image,
            xy=(0, y_position),
            font=self.font,
            padding=(10, 10),
            text=meeting_info.time_info,
            offset=self.meeting_info_time_info_offset
        )
        y_position += self.font.getbbox(text=meeting_info.time_info)[3]

        # Drawing time token
        (l, t, r, b) = self.font.getbbox(text=str(meeting_info.time_token))
        y_position += 20
        self.draw_text_internal(
            image=image,
            xy=(round(image.width / 2 - (r - l)), y_position),
            font=self.font.font_variant(size=44),
            text=str(meeting_info.time_token),
        )

    def draw_free_internal(self, image: Image):
        self.draw_background_internal(
            image=image,
            color=ImageColor.getrgb("ForestGreen")
        )
        if self.message is not None:
            font = self.font.font_variant(size=36)
            (l, t, r, b) = font.getbbox(self.message)
            self.message_offset = self.draw_text_internal(
                image=image,
                xy=(0, round(image.height / 2 - (b - t) / 2)),
                font=font,
                padding=(10, 0),
                text=self.message,
                offset=self.message_offset
            )

    @staticmethod
    def draw_background_internal(image: Image, color: ImageColor):
        draw = ImageDraw(image)
        draw.rounded_rectangle(
            xy=(0, 0, image.width, image.height),
            radius=20,
            fill=color,
        )

    @staticmethod
    def draw_text_internal(image: Image, xy: tuple[int, int], font: ImageFont, text: str,
                           padding: tuple[int, int] or None = None,
                           offset: int = None) -> int:
        if padding is None:
            padding = (0, 0)
        if offset is None:
            offset = 0
        (l, t, r, b) = font.getbbox(text)
        image_for_text = PIL.Image.new(
            mode="RGBA",
            size=(image.width - padding[0] * 2, b + padding[1] * 2),
        )
        text_draw = ImageDraw(image_for_text)
        text_draw.text((offset, 0), text=text, font=font, anchor="lt")

        if r - l > image_for_text.width:
            offset -= 3
            if abs(offset) >= r - l:
                offset = image_for_text.width

        image.paste(
            im=image_for_text,
            box=(xy[0] + padding[0], xy[1] + padding[1]),
            mask=image_for_text
        )
        return offset
