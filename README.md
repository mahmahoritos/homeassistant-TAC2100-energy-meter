# TAC2100 Energy Meter (Home Assistant)

**Status: alpha** (`0.1.0-alpha.2`) — for testing; breaking changes are possible before a stable release.

Custom integration for the **Wenzhou Taiye TAC2100** series power meter using **Modbus** input registers (function `0x04`, IEEE-754 floats) per the manufacturer protocol.

## Features

- **Modbus TCP** (IP + port) and **Modbus RTU** (serial port, baud rate, data bits, parity, stop bits)
- Reads **input registers** (function `0x04`) as **32-bit IEEE-754 floats**, as in the TAC2100 Modbus protocol v1.0 measuring table (not the integer holding-register table)
- Measurements: voltage, current, powers, power factor, frequency, demands, and energy totals
- **Energy dashboard**: import/export **active energy** sensors use `device_class: energy`, `state_class: total_increasing`, and **kWh** as required by the [Home Assistant energy FAQ](https://www.home-assistant.io/docs/energy/faq/#troubleshooting-missing-entities)
- Configurable **kWh offsets** for import and export active energy
- **English** and **Russian** UI strings (Russian entity names/units where applicable)

## Installation

### HACS

1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (category: **Integration**).
2. Install **TAC2100 Energy Meter**.
3. Restart Home Assistant.
4. Add the integration under **Settings → Devices & services → Add integration → TAC2100 Energy Meter**.

### Manual

Copy the `custom_components/tac2100` folder into your Home Assistant `config/custom_components/` directory, restart Home Assistant, then add the integration from the UI.

## Energy configuration

In **Settings → Dashboards → Energy**, use:

- **Grid consumption** → sensor **Total import active energy**
- **Return to grid** (if applicable) → sensor **Total export active energy**

## Requirements

- Home Assistant **2024.1** or newer
- Network or serial access to the meter; set the **Modbus unit ID (slave)** on the connection step (same for TCP and RTU; often `1`)

## Disclaimer

This project is not affiliated with Wenzhou Taiye Electric Co., Ltd. Verify register map and wiring against your device manual.
