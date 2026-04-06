"""Data update coordinator for TAC2100."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_CONNECTION_TYPE,
    CONF_EXPORT_ENERGY_OFFSET,
    CONF_HOST,
    CONF_IMPORT_ENERGY_OFFSET,
    CONF_PARITY,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SERIAL_PORT,
    CONF_SLAVE,
    CONF_STOPBITS,
    CONNECTION_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_PORT_TCP,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DEFAULT_STOPBITS,
    DOMAIN,
    REG_ACTIVE_POWER,
    REG_APPARENT_POWER,
    REG_CURRENT,
    REG_FREQUENCY,
    REG_PHASE_ANGLE,
    REG_POWER_FACTOR,
    REG_REACTIVE_POWER,
    REG_VOLTAGE,
)
from .modbus_client import create_modbus_client, float_at, read_input_registers_block

_LOGGER = logging.getLogger(__name__)

# Input register blocks (function 0x04), float layout per TAC2100 manual
_BLOCK_MAIN_START = 0
_BLOCK_MAIN_COUNT = 50  # through frequency at 0x0030 (+2 regs)
_BLOCK_LOAD_START = 0x004E
_BLOCK_LOAD_COUNT = 2
_BLOCK_DEMAND_START = 0x008C
_BLOCK_DEMAND_COUNT = 40  # through 0x00B3 exclusive -> 0x00B2+2
_BLOCK_ENERGY_START = 0x0500
_BLOCK_ENERGY_COUNT = 14


class Tac2100Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll TAC2100 via Modbus and expose measurements."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        data = entry.data
        self._connection_type = data[CONF_CONNECTION_TYPE]
        self._slave = int(data.get(CONF_SLAVE, DEFAULT_SLAVE))
        self.import_energy_offset = float(data.get(CONF_IMPORT_ENERGY_OFFSET, 0.0))
        self.export_energy_offset = float(data.get(CONF_EXPORT_ENERGY_OFFSET, 0.0))

        interval = int(data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )
        self._client = create_modbus_client(
            self._connection_type,
            host=data.get(CONF_HOST) if self._connection_type == CONNECTION_TCP else None,
            port=int(data.get(CONF_PORT, DEFAULT_PORT_TCP)),
            serial_port=data.get(CONF_SERIAL_PORT) if self._connection_type == CONNECTION_RTU else None,
            baudrate=int(data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE)),
            bytesize=int(data.get(CONF_BYTESIZE, DEFAULT_BYTESIZE)),
            parity=str(data.get(CONF_PARITY, DEFAULT_PARITY)),
            stopbits=int(data.get(CONF_STOPBITS, DEFAULT_STOPBITS)),
        )

    @property
    def slave(self) -> int:
        return self._slave

    async def _ensure_connected(self) -> None:
        if not self._client.connected:
            connected = await self._client.connect()
            if not connected:
                msg = "Could not connect to Modbus device"
                raise UpdateFailed(msg)

    async def _async_update_data(self) -> dict[str, Any]:
        await self._ensure_connected()
        slave = self._slave

        main = await read_input_registers_block(
            self._client, slave, _BLOCK_MAIN_START, _BLOCK_MAIN_COUNT
        )
        load_b = await read_input_registers_block(
            self._client, slave, _BLOCK_LOAD_START, _BLOCK_LOAD_COUNT
        )
        demand = await read_input_registers_block(
            self._client, slave, _BLOCK_DEMAND_START, _BLOCK_DEMAND_COUNT
        )
        energy = await read_input_registers_block(
            self._client, slave, _BLOCK_ENERGY_START, _BLOCK_ENERGY_COUNT
        )

        if main is None or load_b is None or demand is None or energy is None:
            msg = "Modbus read failed"
            raise UpdateFailed(msg)

        def f_main(offset: int) -> float:
            return float_at(main, offset)

        def f_dem(offset: int) -> float:
            return float_at(demand, offset)

        def f_en(offset: int) -> float:
            return float_at(energy, offset)

        # Sanity check primary measurements
        voltage = f_main(REG_VOLTAGE)
        current = f_main(REG_CURRENT)
        if voltage != voltage or current != current:  # NaN check
            msg = "Invalid data from meter"
            raise UpdateFailed(msg)

        return {
            "voltage": f_main(REG_VOLTAGE),
            "current": f_main(REG_CURRENT),
            "active_power": f_main(REG_ACTIVE_POWER),
            "reactive_power": f_main(REG_REACTIVE_POWER),
            "apparent_power": f_main(REG_APPARENT_POWER),
            "power_factor": f_main(REG_POWER_FACTOR),
            "phase_angle": f_main(REG_PHASE_ANGLE),
            "frequency": f_main(REG_FREQUENCY),
            "load_nature": float_at(load_b, 0),
            "active_power_demand": f_dem(0),
            "reactive_power_demand": f_dem(2),
            "apparent_power_demand": f_dem(4),
            "current_demand": f_dem(6),
            "import_active_power_demand": f_dem(14),
            "export_active_power_demand": f_dem(16),
            "max_active_power_demand": f_dem(22),
            "max_reactive_power_demand": f_dem(24),
            "max_apparent_power_demand": f_dem(26),
            "max_current_demand": f_dem(28),
            "max_import_active_power_demand": f_dem(36),
            "max_export_active_power_demand": f_dem(38),
            "total_import_active_energy_raw": f_en(0),
            "total_export_active_energy_raw": f_en(2),
            "total_active_energy_raw": f_en(4),
            "total_import_reactive_energy_raw": f_en(8),
            "total_export_reactive_energy_raw": f_en(10),
            "total_reactive_energy_raw": f_en(12),
        }

    async def async_shutdown(self) -> None:
        """Close Modbus connection."""
        await super().async_shutdown()
        if self._client is not None:
            self._client.close()
