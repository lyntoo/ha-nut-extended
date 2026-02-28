"""Provides buttons for NUT UPS commands."""

from __future__ import annotations

import logging

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NutConfigEntry
from .const import (
    COMMAND_LOAD_OFF,
    COMMAND_SHUTDOWN_REBOOT,
    COMMAND_SHUTDOWN_STAYOFF,
    COMMAND_TEST_BATTERY_START,
    COMMAND_TEST_BATTERY_START_QUICK,
    COMMAND_TEST_BATTERY_STOP,
)
from .entity import NUTBaseEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

# UPS-level command buttons (not outlet-specific)
UPS_BUTTON_DESCRIPTIONS: dict[str, ButtonEntityDescription] = {
    COMMAND_TEST_BATTERY_START_QUICK: ButtonEntityDescription(
        key=COMMAND_TEST_BATTERY_START_QUICK,
        translation_key="test_battery_start_quick",
        entity_registry_enabled_default=True,
    ),
    COMMAND_TEST_BATTERY_START: ButtonEntityDescription(
        key=COMMAND_TEST_BATTERY_START,
        translation_key="test_battery_start",
        entity_registry_enabled_default=True,
    ),
    COMMAND_TEST_BATTERY_STOP: ButtonEntityDescription(
        key=COMMAND_TEST_BATTERY_STOP,
        translation_key="test_battery_stop",
        entity_registry_enabled_default=True,
    ),
    COMMAND_SHUTDOWN_REBOOT: ButtonEntityDescription(
        key=COMMAND_SHUTDOWN_REBOOT,
        translation_key="shutdown_reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_registry_enabled_default=True,
    ),
    COMMAND_SHUTDOWN_STAYOFF: ButtonEntityDescription(
        key=COMMAND_SHUTDOWN_STAYOFF,
        translation_key="shutdown_stayoff",
        entity_registry_enabled_default=True,
    ),
    COMMAND_LOAD_OFF: ButtonEntityDescription(
        key=COMMAND_LOAD_OFF,
        translation_key="load_off",
        entity_registry_enabled_default=True,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: NutConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the NUT buttons."""
    pynut_data = config_entry.runtime_data
    coordinator = pynut_data.coordinator
    status = coordinator.data
    user_available_commands = pynut_data.user_available_commands

    data = pynut_data.data
    unique_id = pynut_data.unique_id
    valid_button_types: dict[str, ButtonEntityDescription] = {}

    # Add UPS-level command buttons
    for cmd, description in UPS_BUTTON_DESCRIPTIONS.items():
        valid_button_types[cmd] = description

    # Dynamically add outlet button types
    if (num_outlets := status.get("outlet.count")) is not None:
        for outlet_num in range(1, int(num_outlets) + 1):
            outlet_num_str = str(outlet_num)
            outlet_name: str = (
                status.get(f"outlet.{outlet_num_str}.name") or outlet_num_str
            )
            outlet_cmd = f"outlet.{outlet_num_str}.load.cycle"
            valid_button_types[outlet_cmd] = ButtonEntityDescription(
                key=outlet_cmd,
                translation_key="outlet_number_load_cycle",
                translation_placeholders={"outlet_name": outlet_name},
                device_class=ButtonDeviceClass.RESTART,
                entity_registry_enabled_default=True,
            )

    async_add_entities(
        NUTButton(coordinator, description, data, unique_id)
        for button_id, description in valid_button_types.items()
        if button_id in user_available_commands
    )


class NUTButton(NUTBaseEntity, ButtonEntity):
    """Representation of a button entity for NUT."""

    async def async_press(self) -> None:
        """Press the button — sends the instcmd to the UPS."""
        await self.pynut_data.async_run_command(self.entity_description.key)
