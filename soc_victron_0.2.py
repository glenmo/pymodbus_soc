#!/usr/bin/env python3
"""
soc_victron.py — pymodbus 3.x compatible

Reads Modbus holding registers (e.g., from a Victron GX device via Modbus TCP)
and prints a simple result. Supports common decode helpers.

Tested with pymodbus==3.11.3
"""

from __future__ import annotations
import sys
import time
import argparse
from typing import List, Optional

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import struct


def decode_registers(
    regs: List[int],
    dtype: str = "u16",
    byteorder: str = "big",
    wordorder: str = "big",
):
    """
    Decode a list of 16-bit registers into a value using struct module.

    dtype options:
      - "u16", "s16"               -> single register
      - "u32", "s32", "f32"        -> two registers
      - "u64", "s64", "f64"        -> four registers

    byteorder/wordorder: "big" or "little"
    """
    if not regs:
        return None

    # Convert registers to bytes
    # Each register is 16 bits (2 bytes)
    byte_data = bytearray()
    
    # Handle word order (order of registers)
    if wordorder == "little":
        regs = list(reversed(regs))
    
    # Convert each register to bytes with specified byte order
    endian_char = '>' if byteorder == 'big' else '<'
    for reg in regs:
        byte_data.extend(struct.pack(f'{endian_char}H', reg))
    
    # Decode based on data type
    format_map = {
        'u16': f'{endian_char}H',  # unsigned short
        's16': f'{endian_char}h',  # signed short
        'u32': f'{endian_char}L',  # unsigned long
        's32': f'{endian_char}l',  # signed long
        'f32': f'{endian_char}f',  # float
        'u64': f'{endian_char}Q',  # unsigned long long
        's64': f'{endian_char}q',  # signed long long
        'f64': f'{endian_char}d',  # double
    }
    
    if dtype not in format_map:
        raise ValueError(f"Unsupported dtype: {dtype}")
    
    format_str = format_map[dtype]
    expected_size = struct.calcsize(format_str)
    
    if len(byte_data) < expected_size:
        raise ValueError(f"Not enough data for {dtype}: need {expected_size} bytes, got {len(byte_data)}")
    
    return struct.unpack(format_str, byte_data[:expected_size])[0]


def read_holding(
    client: ModbusTcpClient,
    address: int,
    count: int = 1,
    slave: int = 100,  # Victron GX commonly uses 100
    retries: int = 2,
    retry_sleep: float = 0.2,
):
    """
    Read holding registers with minimal retries and proper pymodbus 3.x params.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            rr = client.read_holding_registers(address=address, count=count)
            if rr.isError():
                # rr is a Modbus exception response
                raise ModbusIOException(f"Modbus exception: {rr}")
            return rr.registers
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(retry_sleep)
            else:
                break
    # If we get here, all attempts failed
    raise last_exc if last_exc else RuntimeError("Unknown Modbus error")


def main():
    p = argparse.ArgumentParser(description="Read Modbus holding registers (pymodbus 3.x).")
    p.add_argument("--host", default="127.0.0.1", help="Modbus TCP host/IP")
    p.add_argument("--port", type=int, default=502, help="Modbus TCP port (default 502)")
    p.add_argument("--slave", type=int, default=100, help="Slave/Unit ID (Victron GX often 100)")
    p.add_argument("--address", type=int, required=True, help="Register address (0-based)")
    p.add_argument("--count", type=int, default=1, help="Number of 16-bit registers to read")
    p.add_argument("--dtype", default="u16",
                   help='Decode as: u16,s16,u32,s32,f32,u64,s64,f64 (default u16). '
                        'If you just want raw registers, ignore this.')
    p.add_argument("--byteorder", default="big", choices=["big", "little"], help="Byte order")
    p.add_argument("--wordorder", default="big", choices=["big", "little"], help="Word order")
    p.add_argument("--timeout", type=float, default=2.0, help="Socket timeout seconds")
    args = p.parse_args()

    client = ModbusTcpClient(args.host, port=args.port, timeout=args.timeout, unit=args.slave)
    if not client.connect():
        print(f"ERROR: Could not connect to {args.host}:{args.port}", file=sys.stderr)
        sys.exit(2)

    try:
        regs = read_holding(
            client=client,
            address=args.address,
            count=args.count,
            slave=args.slave,
        )
        # Optional decode
        try:
            value = decode_registers(
                regs, dtype=args.dtype, byteorder=args.byteorder, wordorder=args.wordorder
            )
        except Exception:
            value = None

        # Pretty print
        print(f"Host={args.host} Port={args.port} Slave={args.slave} Address={args.address} Count={args.count}")
        print(f"Raw registers: {regs}")
        if value is not None:
            print(f"Decoded ({args.dtype}, byteorder={args.byteorder}, wordorder={args.wordorder}): {value}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()

