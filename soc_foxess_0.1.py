from pymodbus.client import ModbusTcpClient


# Configuration
IP_ADDRESS = "192.168.11.81"
PORT = 502
SOC_REGISTER_ADDRESS = 37612  # From Citation 1, register 309 (SoC related)
SOC_REGISTER_COUNT = 1
MODEL_REGISTER_ADDRESS = 30000  # Model number register
MODEL_REGISTER_COUNT = 2  # Typically 2 registers for model string
SERIAL_REGISTER_ADDRESS = 30016  # Serial number register
SERIAL_REGISTER_COUNT = 2  # Typically 2 registers for serial string

def read_soc():
    # Create Modbus TCP client
    client = ModbusTcpClient(IP_ADDRESS, port=PORT)
    
    try:
        # Connect to the device
        if not client.connect():
            print("Failed to connect to inverter")
            return None
            
        # Read the SoC register (46612)
        response = client.read_holding_registers(
            address=SOC_REGISTER_ADDRESS,
            count=SOC_REGISTER_COUNT,
            unit=1  # Unit ID (typically 1 for inverters)
        )
        
        if response.isError():
            print(f"Modbus error: {response}")
            return None
            
        # Extract the SoC value (assuming it's a U16 register)
        soc_value = response.registers[0]
        print(f"State of Charge (SoC): {soc_value}%")
        
        return soc_value
        
    except Exception as e:
        print(f"Error reading SoC: {e}")
        return None
        
    finally:
        # Close the connection
        client.close()

def read_model():
    # Create Modbus TCP client
    client = ModbusTcpClient(IP_ADDRESS, port=PORT)
    
    try:
        # Connect to the device
        if not client.connect():
            print("Failed to connect to inverter")
            return None
            
        # Read the model number register (30000)
        response = client.read_holding_registers(
            address=MODEL_REGISTER_ADDRESS,
            count=MODEL_REGISTER_COUNT,
            unit=1
        )
        
        if response.isError():
            print(f"Modbus error reading model: {response}")
            return None
            
        # Extract model number (assuming it's a string)
        model_bytes = response.registers
        model_string = ""
        for i in range(len(model_bytes)):
            # Convert register value to 2-character string
            model_string += format(model_bytes[i], '04X')
        
        print(f"Model Number: {model_string}")
        return model_string
        
    except Exception as e:
        print(f"Error reading model: {e}")
        return None
        
    finally:
        # Close the connection
        client.close()

def read_serial():
    # Create Modbus TCP client
    client = ModbusTcpClient(IP_ADDRESS, port=PORT)
    
    try:
        # Connect to the device
        if not client.connect():
            print("Failed to connect to inverter")
            return None
            
        # Read the serial number register (30016)
        response = client.read_holding_registers(
            address=SERIAL_REGISTER_ADDRESS,
            count=SERIAL_REGISTER_COUNT,
            unit=1
        )
        
        if response.isError():
            print(f"Modbus error reading serial: {response}")
            return None
            
        # Extract serial number (assuming it's a string)
        serial_bytes = response.registers
        serial_string = ""
        for i in range(len(serial_bytes)):
            # Convert register value to 2-character string
            serial_string += format(serial_bytes[i], '04X')
        
        print(f"Serial Number: {serial_string}")
        return serial_string
        
    except Exception as e:
        print(f"Error reading serial: {e}")
        return None
        
    finally:
        # Close the connection
        client.close()

def read_all_info():
    """Read all information from inverter"""
    print("Reading inverter information...")
    
    # Read SoC
    soc = read_soc()
    
    # Read model number
    model = read_model()
    
    # Read serial number
    serial = read_serial()
    
    return {
        "soc": soc,
        "model": model,
        "serial": serial
    }

if __name__ == "__main__":
    # Read all information
    results = read_all_info()
    
    print("\n--- Inverter Information ---")
    if results["soc"] is not None:
        print(f"State of Charge (SoC): {results['soc']}%")
    if results["model"] is not None:
        print(f"Model Number: {results['model']}")
    if results["serial"] is not None:
        print(f"Serial Number: {results['serial']}")

