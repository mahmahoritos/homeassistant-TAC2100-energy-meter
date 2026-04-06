"""Config flow for TAC2100."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
)

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
    CONNECTION_RTU,
    CONNECTION_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_EXPORT_ENERGY_OFFSET,
    DEFAULT_IMPORT_ENERGY_OFFSET,
    DEFAULT_NAME,
    DEFAULT_PARITY,
    DEFAULT_PORT_TCP,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DEFAULT_STOPBITS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONNECTION_TYPE): SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(value=CONNECTION_TCP, label="Modbus TCP"),
                    SelectOptionDict(value=CONNECTION_RTU, label="Modbus RTU"),
                ],
                translation_key="connection_type",
            )
        ),
    }
)


def _tcp_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT_TCP): vol.All(int, vol.Range(min=1, max=65535)),
            vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): vol.All(int, vol.Range(min=1, max=247)),
        }
    )


def _rtu_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_SERIAL_PORT): str,
            vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.All(int, vol.Range(min=300, max=921600)),
            vol.Required(CONF_BYTESIZE, default=DEFAULT_BYTESIZE): vol.All(int, vol.In([7, 8])),
            vol.Required(CONF_PARITY, default=DEFAULT_PARITY): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        SelectOptionDict(value="N", label="None"),
                        SelectOptionDict(value="E", label="Even"),
                        SelectOptionDict(value="O", label="Odd"),
                    ],
                    translation_key="parity",
                )
            ),
            vol.Required(CONF_STOPBITS, default=DEFAULT_STOPBITS): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        SelectOptionDict(value=1, label="1"),
                        SelectOptionDict(value=2, label="2"),
                    ],
                    translation_key="stopbits",
                )
            ),
            vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): vol.All(int, vol.Range(min=1, max=247)),
        }
    )


STEP_DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=5, max=3600)
        ),
        vol.Optional(CONF_IMPORT_ENERGY_OFFSET, default=DEFAULT_IMPORT_ENERGY_OFFSET): vol.Coerce(float),
        vol.Optional(CONF_EXPORT_ENERGY_OFFSET, default=DEFAULT_EXPORT_ENERGY_OFFSET): vol.Coerce(float),
    }
)


async def _try_communication(data: dict[str, Any]) -> None:
    """Verify Modbus connectivity and a readable measurement block."""
    # Lazy import: keeps config_flow import light (avoids extra work on event loop import path).
    from .modbus_client import create_modbus_client, read_input_registers_block

    conn = data[CONF_CONNECTION_TYPE]
    client = create_modbus_client(
        conn,
        host=data.get(CONF_HOST) if conn == CONNECTION_TCP else None,
        port=int(data.get(CONF_PORT, DEFAULT_PORT_TCP)),
        serial_port=data.get(CONF_SERIAL_PORT) if conn == CONNECTION_RTU else None,
        baudrate=int(data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE)),
        bytesize=int(data.get(CONF_BYTESIZE, DEFAULT_BYTESIZE)),
        parity=str(data.get(CONF_PARITY, DEFAULT_PARITY)),
        stopbits=int(data.get(CONF_STOPBITS, DEFAULT_STOPBITS)),
    )
    slave = int(data[CONF_SLAVE])
    try:
        connected = await client.connect()
        if not connected:
            msg = "cannot_connect"
            raise ValueError(msg)
        block = await read_input_registers_block(client, slave, 0, 4)
        if block is None or len(block) < 4:
            msg = "cannot_read"
            raise ValueError(msg)
    finally:
        client.close()


class Tac2100ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TAC2100."""

    VERSION = 1

    def __init__(self) -> None:
        self._connection_type: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select Modbus connection type."""
        if user_input is not None:
            self._connection_type = user_input[CONF_CONNECTION_TYPE]
            return await self.async_step_connection()
        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA)

    async def async_step_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter TCP or RTU parameters."""
        assert self._connection_type is not None
        schema = _tcp_schema() if self._connection_type == CONNECTION_TCP else _rtu_schema()
        errors: dict[str, str] = {}

        if user_input is not None:
            self._conn_data = {CONF_CONNECTION_TYPE: self._connection_type, **user_input}
            return await self.async_step_device()

        return self.async_show_form(
            step_id="connection",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Slave ID, polling, energy offsets."""
        if not hasattr(self, "_conn_data"):
            return await self.async_step_user()

        errors: dict[str, str] = {}
        if user_input is not None:
            merged = {**self._conn_data, **user_input}
            try:
                await _try_communication(merged)
            except ValueError as err:
                _LOGGER.debug("Modbus validation failed: %s", err)
                errors["base"] = str(err)
            else:
                await self.async_set_unique_id(_unique_id_from_config(merged))
                self._abort_if_unique_id_configured()
                title = _entry_title(merged)
                return self.async_create_entry(title=title, data=merged)

        return self.async_show_form(
            step_id="device",
            data_schema=STEP_DEVICE_SCHEMA,
            errors=errors,
        )


def _unique_id_from_config(data: dict[str, Any]) -> str:
    """Build a stable unique ID for this meter connection."""
    conn = data[CONF_CONNECTION_TYPE]
    slave = int(data[CONF_SLAVE])
    if conn == CONNECTION_TCP:
        return f"tcp_{data[CONF_HOST]}_{int(data[CONF_PORT])}_{slave}"
    return f"rtu_{data[CONF_SERIAL_PORT]}_{int(data[CONF_BAUDRATE])}_{slave}"


def _entry_title(data: dict[str, Any]) -> str:
    conn = data[CONF_CONNECTION_TYPE]
    if conn == CONNECTION_TCP:
        return f"{DEFAULT_NAME} ({data[CONF_HOST]})"
    return f"{DEFAULT_NAME} ({data[CONF_SERIAL_PORT]})"
