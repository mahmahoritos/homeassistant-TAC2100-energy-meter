"""Modbus helpers for TAC2100."""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymodbus.client import AsyncModbusBaseClient


def registers_to_float(regs: list[int]) -> float:
    """Decode two big-endian Modbus registers as IEEE754 float (high word first)."""
    if len(regs) < 2:
        msg = "Expected at least 2 registers"
        raise ValueError(msg)
    word_h, word_l = regs[0] & 0xFFFF, regs[1] & 0xFFFF
    payload = bytes([(word_h >> 8) & 0xFF, word_h & 0xFF, (word_l >> 8) & 0xFF, word_l & 0xFF])
    return struct.unpack(">f", payload)[0]


async def read_input_registers_block(
    client: AsyncModbusBaseClient, device_id: int, address: int, count: int
) -> list[int] | None:
    """Read a block of input registers."""
    result = await client.read_input_registers(address=address, count=count, device_id=device_id)
    if result.isError() or result.registers is None:
        return None
    return list(result.registers)


def float_at(block: list[int], reg_offset: int) -> float:
    """Extract float from block starting at reg_offset (relative to block start)."""
    return registers_to_float(block[reg_offset : reg_offset + 2])


def create_modbus_client(
    connection_type: str,
    *,
    host: str | None = None,
    port: int = 502,
    serial_port: str | None = None,
    baudrate: int = 9600,
    bytesize: int = 8,
    parity: str = "N",
    stopbits: int = 1,
):
    """Build async Modbus client for RTU or TCP."""
    if connection_type == "tcp":
        from pymodbus.client import AsyncModbusTcpClient

        return AsyncModbusTcpClient(host, port=port, timeout=5)
    if connection_type == "rtu":
        from pymodbus.client import AsyncModbusSerialClient

        return AsyncModbusSerialClient(
            serial_port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=5,
        )
    msg = f"Unknown connection type: {connection_type}"
    raise ValueError(msg)
