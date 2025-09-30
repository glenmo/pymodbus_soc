from pymodbus.client import ModbusTcpClient

# Configuration
inverter_ip = '192.168.11.215'  # Replace with your inverter's IP address
port = 502  # Default Modbus TCP port
registers = {
    'battery_charge_current': 33143,
    'battery_discharge_current': 33144,
    'inverter_temperature': 33093
}

# Initialize Modbus client (pymodbus 3.x uses keyword-only args beyond host)
client = ModbusTcpClient(inverter_ip, port=port)
connected = client.connect()
if not connected:
    raise RuntimeError(f"Unable to connect to Modbus server at {inverter_ip}:{port}")

# Function to read register
def read_register(register):
    rr = client.read_input_registers(address=register, count=1)
    if rr.isError():
        print(f"Error reading register {register}: {rr}")
        return None
    return rr.registers[0]

# Read and display values
for name, register in registers.items():
    value = read_register(register)
    if value is not None:
        print(f"{name.replace('_', ' ').title()}: {value}")

# Close connection
client.close()
