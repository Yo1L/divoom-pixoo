import asyncio  # noqa: D100
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.template import Template, TemplateError

from . import DOMAIN
from .pages.custom import PageCustom
from .pixoo import Pixoo
from .schemas.page_schema import PAGE_SCHEMA

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Optional("scan_interval"): cv.time_period,
        vol.Required("pages"): vol.All(cv.ensure_list, [PAGE_SCHEMA]),
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    if discovery_info is None:
        discovery_info = config.get(DOMAIN)
    if discovery_info is None:
        return
    ip_address = discovery_info[CONF_IP_ADDRESS]
    pages = discovery_info.get("pages", [])
    for page in pages:
        condition_template = page.get("condition")
        if condition_template is not None:
            try:
                page["condition_template"] = Template(condition_template, hass)
            except (TemplateError, ValueError) as e:
                _LOGGER.error("Error in condition template: %s", e)
                page["condition_template"] = None

    scan_interval_config = discovery_info.get("scan_interval")
    _LOGGER.debug("Scan interval config: %s", scan_interval_config)
    if isinstance(scan_interval_config, dict):
        scan_interval = timedelta(**scan_interval_config)
    elif scan_interval_config is not None:
        scan_interval = timedelta(seconds=int(scan_interval_config))
    else:
        _LOGGER.error(
            "Scan interval is not defined, falling back to default of 30 seconds"
        )
        scan_interval = timedelta(seconds=30)
    _LOGGER.debug("Scan interval config: %s", scan_interval_config)
    _LOGGER.debug("Scan interval: %s", scan_interval)

    entity = PixooEntity(ip_address, pages, scan_interval)
    async_add_entities([entity], True)

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        "show_message",
        {
            vol.Required("messages"): [cv.string],
            vol.Required("positions"): [[cv.positive_int]],
            vol.Required("colors"): [[cv.positive_int]],
            vol.Required("fonts"): [cv.string],
            vol.Optional("images", default=[]): [cv.string],
            vol.Optional("image_positions", default=[]): [[cv.positive_int]],
        },
        "async_show_message",
    )


class PixooEntity(Entity):
    def __init__(self, ip_address, pages, scan_interval):  # noqa: D107
        self._ip_address = ip_address
        self._pages = pages
        self._scan_interval = scan_interval
        self._current_page_index = 0
        self._current_page = self._pages[self._current_page_index]
        self._attr_name = "divoom_pixoo"
        self._attr_extra_state_attributes = {}
        self._attr_extra_state_attributes["page"] = self._current_page["page"]
        _LOGGER.debug(pages)
        self.showing_notification = False

    async def async_added_to_hass(self):
        if DOMAIN in self.hass.data:
            self.hass.data[DOMAIN].setdefault("entities", []).append(self)

        self._update_interval = async_track_time_interval(
            self.hass, self._async_update, self._scan_interval
        )

    async def async_will_remove_from_hass(self):
        """When entity is being removed from hass."""
        if self._update_interval is not None:
            self._update_interval()
            self._update_interval = None

    async def _async_update(self, now=None):
        _LOGGER.debug("Update called at %s", now)
        await self._async_update_data()

    async def _async_update_data(self):
        if self.showing_notification:
            return

        self._current_page = self._pages[self._current_page_index]
        current_page_data = self._pages[self._current_page_index]
        _LOGGER.debug("current page: {current_page_data}")
        self._attr_extra_state_attributes["page"] = current_page_data["page"]

        if "condition_template" in current_page_data:
            condition = current_page_data["condition_template"]
            condition.hass = self.hass
            try:
                if not condition.async_render():
                    self._current_page_index = (self._current_page_index + 1) % len(
                        self._pages
                    )
                    return
            except TemplateError as e:
                _LOGGER.error("Error rendering condition template: %s", e)
                self._current_page_index = (self._current_page_index + 1) % len(
                    self._pages
                )
                return

        def update():
            pixoo = Pixoo(self._ip_address)

            if "channel" in current_page_data:
                for ch in current_page_data["channel"]:
                    pixoo.set_custom_page(ch["number"])

            if "clockId" in current_page_data:
                for clock in current_page_data["clockId"]:
                    pixoo.set_clock(clock["number"])

            if "custom" in current_page_data:
                page_custom = PageCustom(pixoo, self.hass)
                page_custom.render(current_page_data["custom"])

        await self.hass.async_add_executor_job(update)
        self._current_page_index = (self._current_page_index + 1) % len(self._pages)

    async def async_show_message(
        self, messages, positions, colors, fonts, images=None, image_positions=None
    ):
        if not all([messages, positions, colors, fonts]) or len(messages) != len(
            positions
        ) != len(colors) != len(fonts):
            _LOGGER.error(
                "Lists for messages, positions, colors, and fonts must all be present and have the same length"
            )
            return

        self.showing_notification = True

        def draw():
            pixoo = Pixoo(self._ip_address)

            for message, position, color, font in zip(
                messages, positions, colors, fonts
            ):
                pixoo.send_text(message, tuple(position))

        await self.hass.async_add_executor_job(draw)
        await asyncio.sleep(self._scan_interval.total_seconds())
        self.showing_notification = False

    @property
    def state(self):
        return self._current_page["page"]
