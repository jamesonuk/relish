"""Defines a base Relish entity."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RelishCoordinator
from .relish import RelishChild


class RelishEntity(CoordinatorEntity[RelishCoordinator]):
    """Defines a base Relish entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RelishCoordinator,
        iac: str,
        description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._iac = iac
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, iac)},
            name=self.child.name,
            model="child",
            manufacturer="me",
        )
        self.entity_description = description
        self._attr_unique_id = f"{iac}-{description.key}"

    @property
    def child(self) -> RelishChild:
        """Return the device."""
        return self.coordinator.data[self._iac]
