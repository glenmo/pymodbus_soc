# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This project enables reading State of Charge (SOC) from various inverter/battery systems on local networks via Modbus TCP (port 502). It provides vendor-agnostic monitoring tools for the Smart Energy Lab's local LAN environment.

## Architecture

The codebase follows a modular approach with separate readers for different inverter brands:

- **Brand-specific readers**: `soc_foxess_0.1.py`, `soc_victron_0.1.py`, `soc_victron_0.2.py` - Tailored implementations for specific inverter manufacturers
- **Generic reader**: `generic_modbus_reader.py` - Universal Modbus TCP client with extensive configuration options
- **Core dependency**: All scripts use `pymodbus` (v3.x compatible) for Modbus communication

### Key Components

**FoxESS Reader** (`soc_foxess_0.1.py`):
- Reads SOC from register 37612, model from 30000, serial from 30016
- Includes functions: `read_soc()`, `read_model()`, `read_serial()`, `read_all_info()`
- Hardcoded for IP 192.168.11.81

**Victron Readers**:
- `soc_victron_0.1.py`: Simple implementation with hardcoded GX IP 192.168.11.118, Unit ID 100
- `soc_victron_0.2.py`: Advanced version with CLI arguments, register decoding, and retry logic

**Generic Reader** (`generic_modbus_reader.py`):
- Full-featured CLI tool supporting all Modbus register types
- Handles 16-bit and 32-bit values, big/little endian conversion
- Includes register address parsing (40001-49999 for holding registers, etc.)
- Supports scaling factors and debug output

## Common Development Commands

### Running Scripts

**Run FoxESS reader:**
```pwsh
python soc_foxess_0.1.py
```

**Run Victron reader (simple):**
```pwsh
python soc_victron_0.1.py
```

**Run Victron reader (advanced):**
```pwsh
python soc_victron_0.2.py --host 192.168.1.100 --address 840 --count 1 --dtype u16
```

**Run generic Modbus reader:**
```pwsh
# Read single holding register
python generic_modbus_reader.py --ip 192.168.1.100 --register 40001

# Read multiple registers with 32-bit interpretation
python generic_modbus_reader.py --ip 192.168.1.100 --register 40001 --count 2 --bit-length 32

# Read with scaling and debug output
python generic_modbus_reader.py --ip 192.168.1.100 --register 40001 --scale 0.1 --debug
```

### Installing Dependencies

```pwsh
pip install pymodbus==3.*
```

## Network Configuration

- **Default Modbus TCP Port**: 502
- **Common Unit IDs**: 1 (most inverters), 100 (Victron GX devices)
- **Example IP addresses** in code: 192.168.11.81 (FoxESS), 192.168.11.118 (Victron)

## Modbus Register Types

The generic reader supports standard Modbus addressing:
- **40001-49999**: Holding registers (read/write)
- **30001-39999**: Input registers (read-only)
- **10001-19999**: Coils (discrete outputs)
- **20001-29999**: Discrete inputs

## Error Handling Patterns

All readers implement:
- Connection verification before register reads
- Modbus error response checking with `result.isError()`
- Exception handling for network/communication issues
- Proper client cleanup in `finally` blocks

## Development Notes

- Scripts are designed for pymodbus v3.x (current versions)
- Unit ID configuration varies by device (set `client.unit_id` for v3.x)
- Use `--no-pager` flag with git commands when needed
- 32-bit values require reading 2 consecutive 16-bit registers