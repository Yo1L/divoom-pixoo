# noqa: D100
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.template import Template

from ..pixoo64._font import FONT_GICKO, FONT_PICO_8

_LOGGER = logging.getLogger(__name__)


def page_custom(pixoo, hass: HomeAssistant, page_data):  # noqa: D103
    for custom in page_data["custom"]:
        if "texts" in custom:
            for text in custom["texts"]:
                draw_text(pixoo, hass, text)

        if "images" in custom:
            for image in custom["images"]:
                pixoo.draw_image(image["image"], tuple(image["position"]))


def draw_text(pixoo, hass: HomeAssistant, custom):  # noqa: D103
    try:
        text = str(Template(custom["text"], hass).async_render())
        font_color = Template(custom["font_color"], hass).async_render()

    except TemplateError as e:
        _LOGGER.error("Template render error: %s", e)
        text = "Template Error"
        return

    font = FONT_PICO_8
    if "font" in custom and custom["font"] == "small":
        text = text.upper()
        font = FONT_GICKO

    pixoo.draw_text(
        text,
        tuple(custom["position"]),
        font_color,
        font,
    )
