# pip install pymodbus==3.*
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

GX_IP = "192.168.11.118"   # <-- your GX IP
UNIT_ID = 100            # e.g., com.victronenergy.system; change as needed
ADDRESS = 3              # starting register address
COUNT = 2                # how many registers to read (16-bit each)

def main():
    client = ModbusTcpClient(host=GX_IP, port=502)
    try:
        if not client.connect():
            raise RuntimeError("Unable to connect to GX on port 502")

        # Read holding registers (FC=3). Use read_input_registers for FC=4 if required.
        rr = client.read_holding_registers(address=ADDRESS, count=COUNT, unit=UNIT_ID)

        if rr.isError():
            raise ModbusException(f"Modbus error: {rr}")

        regs = rr.registers  # list of 16-bit integers
        print(f"Raw registers @{ADDRESS} (count {COUNT}): {regs}")

        # Example: if the manual says the value is scaled by 10, divide accordingly:
        # value = regs[0] / 10.0
        # print('Scaled value:', value)

    finally:
        client.close()

if __name__ == "__main__":
    main()

