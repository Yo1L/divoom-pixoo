import voluptuous as vol

from homeassistant.helpers import config_validation as cv

TEXT_SCHEMA = vol.Schema(
    {
        vol.Required("text"): cv.template,
        vol.Required("position"): vol.All(
            cv.ensure_list, [cv.positive_int], vol.Length(min=2, max=2)
        ),
        vol.Required("font"): cv.string,
        vol.Required("font_color"): cv.template,
    }
)

IMAGE_SCHEMA = vol.Schema(
    {
        vol.Required("image"): cv.string,
        vol.Required("position"): vol.All(
            cv.ensure_list, [cv.positive_int], vol.Length(min=2, max=2)
        ),
    }
)

CUSTOM_SCHEMA = vol.Schema(
    {
        vol.Optional("background"): cv.string,
        vol.Optional("texts"): vol.All(cv.ensure_list, [TEXT_SCHEMA]),
    }
)
