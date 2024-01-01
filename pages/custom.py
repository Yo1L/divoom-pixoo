# noqa: D100
import logging

from glitch_this import ImageGlitcher
from PIL import Image, ImageDraw

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.template import Template

from ..pixoo import Pixoo

_LOGGER = logging.getLogger(__name__)


class PageCustom:  # noqa: D101
    __pixoo = None
    __hass = None

    def __init__(self, pixoo: Pixoo, hass: HomeAssistant) -> None:  # noqa: D103, D107
        self.__pixoo = pixoo
        self.__hass = hass

    def render(self, page_data):  # noqa: D103
        if "background" in page_data:
            img = Image.open(page_data["background"])
        else:
            img = Image.new("RGB", (64, 64), color="#ffccdd")

        draw = ImageDraw.Draw(img)

        if "texts" in page_data:
            for text in page_data["texts"]:
                self.__draw_text(draw, text)

        if "lines" in page_data:
            for line in page_data["lines"]:
                draw.line(
                    xy=(tuple(line["from"]), tuple(line["to"])),
                    fill=line["color"],
                )

        if "glitch" in page_data:
            speed = 60
            if "speed" in page_data["glitch"]:
                speed = page_data["glitch"]["speed"]

            self.__pixoo.send_images(
                self.__glitch_images(img, page_data["glitch"]), speed=speed
            )
        else:
            self.__pixoo.send_image(img)

    def __glitch_images(self, img: Image, conf):
        frames = 10
        amount = 1

        if "frames" in conf:
            frames = conf["frames"]

        if "amount" in conf:
            amount = conf["amount"]

        return ImageGlitcher().glitch_image(
            img, amount, color_offset=True, gif=True, frames=frames
        )

    def __draw_text(self, draw: ImageDraw, custom):  # noqa: D103
        try:
            text = str(Template(custom["text"], self.__hass).async_render())
            color = Template(custom["color"], self.__hass).async_render()

        except TemplateError as e:
            _LOGGER.error("Template render error: %s", e)
            text = "Template Error"
            return

        draw.text(text=text, xy=tuple(custom["position"]), fill=color)
