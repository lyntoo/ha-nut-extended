"""Provides switches for NUT: outlet power control and UPS beeper."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NutConfigEntry
from .const import COMMAND_BEEPER_DISABLE, COMMAND_BEEPER_ENABLE
from .entity import NUTBaseEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

_BEEPER_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="ups.beeper.status",
    translation_key="beeper",
    entity_registry_enabled_default=True,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: NutConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the NUT switches."""
    pynut_data = config_entry.runtime_data
    coordinator = pynut_data.coordinator
    status = coordinator.data
    data = pynut_data.data
    unique_id = pynut_data.unique_id
    user_available_commands = pynut_data.user_available_commands

    entities: list[NUTBaseEntity] = []

    # Add beeper switch if device reports beeper status and supports the commands
    if (
        COMMAND_BEEPER_ENABLE in user_available_commands
        and COMMAND_BEEPER_DISABLE in user_available_commands
        and "ups.beeper.status" in status
    ):
        entities.append(
            NUTBeeperSwitch(coordinator, _BEEPER_SWITCH_DESCRIPTION, data, unique_id)
        )

    # Dynamically add outlet switch types
    if (num_outlets := status.get("outlet.count")) is not None:
        switch_descriptions = [
            SwitchEntityDescription(
                key=f"outlet.{outlet_num!s}.load.poweronoff",
                translation_key="outlet_number_load_poweronoff",
                translation_placeholders={
                    "outlet_name": status.get(f"outlet.{outlet_num!s}.name")
                    or str(outlet_num)
                },
                device_class=SwitchDeviceClass.OUTLET,
                entity_registry_enabled_default=True,
            )
            for outlet_num in range(1, int(num_outlets) + 1)
            if (
                status.get(f"outlet.{outlet_num!s}.switchable") == "yes"
                and f"outlet.{outlet_num!s}.load.on" in user_available_commands
                and f"outlet.{outlet_num!s}.load.off" in user_available_commands
            )
        ]
        entities.extend(
            NUTSwitch(coordinator, description, data, unique_id)
            for description in switch_descriptions
        )

    async_add_entities(entities)


class NUTBeeperSwitch(NUTBaseEntity, SwitchEntity):
    """Switch that enables or disables the UPS beeper/buzzer."""

    @property
    def is_on(self) -> bool | None:
        """Return True if the beeper is currently enabled."""
        beeper_status = self.coordinator.data.get("ups.beeper.status")
        if beeper_status is None:
            return None
        return beeper_status == "enabled"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the UPS beeper."""
        await self.pynut_data.async_run_command(COMMAND_BEEPER_ENABLE)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the UPS beeper."""
        await self.pynut_data.async_run_command(COMMAND_BEEPER_DISABLE)


class NUTSwitch(NUTBaseEntity, SwitchEntity):
    """Representation of a switch entity for NUT outlet status values."""

    @property
    def is_on(self) -> bool | None:
        """Return the state of the switch."""
        status = self.coordinator.data
        outlet, outlet_num_str = self.entity_description.key.split(".", 2)[:2]
        if (state := status.get(f"{outlet}.{outlet_num_str}.status")) is None:
            return None
        return bool(state == "on")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the outlet."""
        outlet, outlet_num_str = self.entity_description.key.split(".", 2)[:2]
        command_name = f"{outlet}.{outlet_num_str}.load.on"
        await self.pynut_data.async_run_command(command_name)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the outlet."""
        outlet, outlet_num_str = self.entity_description.key.split(".", 2)[:2]
        command_name = f"{outlet}.{outlet_num_str}.load.off"
        await self.pynut_data.async_run_command(command_name)
