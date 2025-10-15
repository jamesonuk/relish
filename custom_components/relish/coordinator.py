"""Support for Relish School Meals."""

from datetime import timedelta

from aiohttp import ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import _LOGGER
from .relish import RelishAPI, RelishChild

SCAN_INTERVAL = timedelta(days=1)


type RelishConfigEntry = ConfigEntry[RelishCoordinator]


class RelishCoordinator(DataUpdateCoordinator[dict[str, RelishChild]]):
    """Base coordinator for Relish."""

    config_entry: RelishConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: RelishConfigEntry,
        session: ClientSession,
    ) -> None:
        """Initialize the scanner."""
        super().__init__(
            hass,
            _LOGGER,
            name=entry.title,
            config_entry=entry,
            update_interval=SCAN_INTERVAL,
        )
        self.api = RelishAPI(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            entry.data[CONF_URL],
            session,
        )

    async def _async_update_data(self) -> dict[str, RelishChild]:
        """Update device data."""
        return await self.api.get_data()
