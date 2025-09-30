#!/usr/bin/env python3
"""
Modbus TCP Register Reader (Corrected for pymodbus v3.0+)

Reads specific Modbus registers from a device via TCP/IP.
Compatible with current versions of pymodbus (v3.0+).

Usage:
    python modbus_reader.py --ip 192.168.1.100 --port 502 --register 40001 --count 1

Arguments:
    --ip: Device IP address (default: 127.0.0.1)
    --port: Modbus TCP port (default: 502)
    --register: Register address (e.g., 40001, 30002)
    --count: Number of registers to read (default: 1)
    --unit: Modbus slave ID (default: 1)
    --type: Register type (holding_registers, input_registers, coils, discrete_inputs)
    --debug: Enable debug output
"""

import argparse
import sys
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_register_address(register_str):
    """
    Parse register address string (e.g., 40001) and return the actual register number.
    """
    try:
        reg_num = int(register_str)
        
        if 40001 <= reg_num <= 49999:
            return reg_num - 40000, "holding_registers"
        elif 30001 <= reg_num <= 39999:
            return reg_num - 30000, "input_registers"
        elif 10001 <= reg_num <= 19999:
            return reg_num - 10000, "coils"
        elif 20001 <= reg_num <= 29999:
            return reg_num - 20000, "discrete_inputs"
        else:
            raise ValueError(f"Register address {reg_num} is out of valid range")
            
    except ValueError as e:
        raise ValueError(f"Invalid register format: {register_str}. "
                        "Use format like 40001, 30002, etc.")

def main():
    parser = argparse.ArgumentParser(
        description="Read specific Modbus registers from a device via TCP/IP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python modbus_reader.py --ip 192.168.1.100 --register 40001
    python modbus_reader.py --ip 192.168.1.100 --register 40001 --count 2
    python modbus_reader.py --ip 192.168.1.100 --register 30002 --type input_registers --count 2
        """
    )
    
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Device IP address (default: 127.0.0.1)")
    
    parser.add_argument("--port", type=int, default=502,
                        help="Modbus TCP port (default: 502)")
    
    parser.add_argument("--register", type=str, required=True,
                        help="Register address (e.g., 40001, 30002)")
    
    parser.add_argument("--count", type=int, default=1,
                        help="Number of registers to read (default: 1)")
    
    parser.add_argument("--unit", type=int, default=1,
                        help="Modbus slave ID (default: 1)")
    
    parser.add_argument("--type", type=str, choices=["coils", "discrete_inputs", "holding_registers", "input_registers"],
                        default="holding_registers",
                        help="Register type (default: holding_registers)")
    
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")
    
    args = parser.parse_args()
    
    # Set up debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Parse register address
    try:
        register_num, register_type = parse_register_address(args.register)
        logger.info(f"Register address {args.register} parsed as register {register_num} "
                   f"of type {register_type}")
    except ValueError as e:
        logger.error(f"Error parsing register address: {e}")
        sys.exit(1)
    
    # Validate count
    if args.count < 1:
        logger.error("Count must be at least 1")
        sys.exit(1)
    
    # Validate unit ID
    if args.unit < 1 or args.unit > 255:
        logger.error("Unit ID must be between 1 and 255")
        sys.exit(1)
    
    # Create Modbus client
    client = ModbusTcpClient(
        host=args.ip,
        port=args.port,
        timeout=5,
        retries=3,
        # No retry_on_empty (removed)
    )
    
    logger.info(f"Connecting to {args.ip}:{args.port} (unit: {args.unit})")
    
    try:
        # Connect to device
        if not client.connect():
            logger.error(f"Failed to connect to {args.ip}:{args.port}")
            sys.exit(1)
        
        logger.info(f"Connected successfully to {args.ip}:{args.port}")
        
        # Set the unit ID on the client (this is how it works in v3.0+)
        client.unit_id = args.unit
        
        # Read registers based on type
        if args.type == "holding_registers":
            result = client.read_holding_registers(
                address=register_num,
                count=args.count
                # No 'unit' argument here
            )
        elif args.type == "input_registers":
            result = client.read_input_registers(
                address=register_num,
                count=args.count
                # No 'unit' argument here
            )
        elif args.type == "coils":
            result = client.read_coils(
                address=register_num,
                count=args.count
                # No 'unit' argument here
            )
        elif args.type == "discrete_inputs":
            result = client.read_discrete_inputs(
                address=register_num,
                count=args.count
                # No 'unit' argument here
            )
        
        # Check for errors
        if not result.isError():
            logger.info(f"Successfully read {len(result.registers)} registers")
            
            # Display results
            if args.count == 1:
                print(f"Register {args.register} value: {result.registers[0]}")
            else:
                print(f"Registers {args.register} to {args.register + args.count - 1}:")
                for i, value in enumerate(result.registers):
                    reg_addr = register_num + i
                    print(f"  Register {reg_addr}: {value}")
                    
        else:
            logger.error(f"Modbus error: {result}")
            sys.exit(1)
            
    except ModbusException as e:
        logger.error(f"Modbus communication error: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        # Always close the connection
        client.close()
        logger.info("Connection closed")

if __name__ == "__main__":
    main()

