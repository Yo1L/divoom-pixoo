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
