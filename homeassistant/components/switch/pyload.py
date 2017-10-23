"""
Support for setting the pyLoad download speed limit.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.pyload/
"""
import logging

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST, CONF_NAME, CONF_PORT, CONF_PASSWORD, CONF_USERNAME, STATE_OFF,
    STATE_ON)
from homeassistant.helpers.entity import ToggleEntity
import homeassistant.helpers.config_validation as cv

_LOGGING = logging.getLogger(__name__)

DEFAULT_NAME = 'pyLoad limit download speed'
DEFAULT_PORT = 8000

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_USERNAME): cv.string,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the pyLoad switch."""
    import pyloadrpc
    from pyloadrpc.error import pyLoadError

    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    port = config.get(CONF_PORT)

    pyload_api = pyloadrpc.Client(
        host, port=port, user=username, password=password)
    try:
        pyload_api.session_stats()
    except pyLoadError:
        _LOGGING.error("Connection to pyLoad API failed")
        return False

    add_devices([pyLoadSwitch(pyload_api, name)])


class pyLoadSwitch(ToggleEntity):
    """Representation of a pyLoad switch."""

    def __init__(self, pyLoad_client, name):
        """Initialize the pyLoad switch."""
        self._name = name
        self.pyLoad_client = pyLoad_client
        self._state = STATE_OFF

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def should_poll(self):
        """Poll for status regularly."""
        return True

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == STATE_ON

    def turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGING.debug("Turning limit download speed of pyLoad on")
        self.pyload_client.set_session(alt_speed_enabled=True)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGING.debug("Turning limit download speed of pyLoad off")
        self.pyload_client.set_session(alt_speed_enabled=False)

    def update(self):
        """Get the latest data from pyLoad and updates the state."""
        active = self.pyload_client.get_session().alt_speed_enabled
        self._state = STATE_ON if active else STATE_OFF