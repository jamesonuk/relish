"""Support for sensors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import RelishConfigEntry
from .entity import RelishEntity

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class RelishSensorEntityDescription(SensorEntityDescription):
    """Relish sensor entity description."""


SENSORS: Final = (
    RelishSensorEntityDescription(
        key="balance",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="GBP",
        name="Account Balance",
        icon="mdi:cash",
    ),
    RelishSensorEntityDescription(
        key="meal_today",
        name="Meal Today",
        icon="mdi:food",
    ),
    RelishSensorEntityDescription(
        key="pudding_today",
        name="Pudding Today",
        icon="mdi:cupcake",
    ),
    RelishSensorEntityDescription(
        key="meal_tomorrow",
        name="Meal Tomorrow",
        icon="mdi:food",
    ),
    RelishSensorEntityDescription(
        key="pudding_tomorrow",
        name="Pudding Tomorrow",
        icon="mdi:cupcake",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RelishConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Relish sensors based on a config entry."""

    coordinator = entry.runtime_data

    known_children: set[str] = set()

    def _check_child() -> None:
        current_children = set(coordinator.data)
        new_children = current_children - known_children
        if new_children:
            known_children.update(new_children)
            async_add_entities(
                RelishSensorEntity(coordinator, iac, sensor_desc)
                for sensor_desc in SENSORS
                for iac in new_children
            )

    _check_child()
    entry.async_on_unload(coordinator.async_add_listener(_check_child))


class RelishSensorEntity(RelishEntity, SensorEntity):
    """Sensor device."""

    entity_description: SensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Get value."""
        if self.entity_description.key == "balance":
            return self.child.account_balance
        if self.entity_description.key == "meal_today":
            return self.child.meal_today
        if self.entity_description.key == "pudding_today":
            return self.child.pudding_today
        if self.entity_description.key == "meal_tomorrow":
            return self.child.meal_tomorrow
        if self.entity_description.key == "pudding_tomorrow":
            return self.child.pudding_tomorrow
        raise ValueError
