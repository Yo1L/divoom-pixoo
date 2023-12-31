import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .channel_schema import CHANNEL_SCHEMA
from .clockid_schema import CLOCKID_SCHEMA
from .image_schema import IMAGE_SCHEMA
from .text_schema import TEXT_SCHEMA

PAGE_SCHEMA = vol.Schema(
    {
        vol.Required("page"): cv.positive_int,
        vol.Optional("condition"): cv.template,
        vol.Optional("texts"): vol.All(cv.ensure_list, [TEXT_SCHEMA]),
        vol.Optional("images"): vol.All(cv.ensure_list, [IMAGE_SCHEMA]),
        vol.Optional("channel"): vol.All(cv.ensure_list, [CHANNEL_SCHEMA]),
        vol.Optional("clockId"): vol.All(cv.ensure_list, [CLOCKID_SCHEMA]),
    }
)
