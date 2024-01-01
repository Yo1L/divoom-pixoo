import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .channel_schema import CHANNEL_SCHEMA
from .clockid_schema import CLOCKID_SCHEMA
from .custom_schema import CUSTOM_SCHEMA

PAGE_SCHEMA = vol.Schema(
    {
        vol.Required("page"): cv.positive_int,
        vol.Optional("condition"): cv.template,
        vol.Optional("custom"): vol.All(cv.ensure_list, [CUSTOM_SCHEMA]),
        vol.Optional("channel"): vol.All(cv.ensure_list, [CHANNEL_SCHEMA]),
        vol.Optional("clockId"): vol.All(cv.ensure_list, [CLOCKID_SCHEMA]),
    }
)
