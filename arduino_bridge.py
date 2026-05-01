"""
AgriSense AI — Arduino Bridge
Run this script ALONGSIDE Streamlit to control pump via serial port.
Usage: python arduino_bridge.py
"""

import time
import sys

# Try to import serial; if not available, give instructions
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# ─── CONFIG ──────────────────────────────────────────────────────────────────
PORTS = ["COM3", "COM4", "/dev/ttyUSB0", "/dev/ttyACM0"]
BAUD  = 9600

def find_port():
    if not SERIAL_AVAILABLE:
        return None
    for port in PORTS:
        try:
            s = serial.Serial(port, BAUD, timeout=1)
            s.close()
            return port
        except Exception:
            continue
    return None

def pump_on(ser):
    if ser:
        ser.write(b"PUMP_ON\n")
        print("[AgriSense] ✅ PUMP ON command sent")

def pump_off(ser):
    if ser:
        ser.write(b"PUMP_OFF\n")
        print("[AgriSense] 🛑 PUMP OFF command sent")

def read_sensors(ser):
    """Read sensor data from Arduino if available."""
    if ser and ser.in_waiting:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        return line
    return None

def main():
    if not SERIAL_AVAILABLE:
        print("⚠️  pyserial not installed.")
        print("    Install with: pip install pyserial")
        print("    Running in simulation mode...\n")
        simulate_loop()
        return

    port = find_port()
    if not port:
        print("⚠️  No Arduino found on any port.")
        print("    Tried:", PORTS)
        print("    Running in simulation mode...\n")
        simulate_loop()
        return

    print(f"✅ Connected to Arduino on {port}")
    try:
        with serial.Serial(port, BAUD, timeout=1) as ser:
            time.sleep(2)  # Arduino reset
            print("AgriSense Bridge running. Press Ctrl+C to stop.")
            print("Commands: 'on' = pump on | 'off' = pump off | 'r' = read sensors\n")
            while True:
                user_input = input("Command: ").strip().lower()
                if user_input == "on":
                    pump_on(ser)
                elif user_input == "off":
                    pump_off(ser)
                elif user_input == "r":
                    data = read_sensors(ser)
                    print(f"Sensor data: {data}" if data else "No data received")
                elif user_input == "q":
                    print("Exiting...")
                    break
                else:
                    print("Unknown command. Use: on | off | r | q")
    except KeyboardInterrupt:
        print("\nBridge stopped.")

def simulate_loop():
    """Simulation mode when no Arduino is connected."""
    print("=== SIMULATION MODE ===")
    print("Commands: 'on' = pump on | 'off' = pump off | 'q' = quit\n")
    pump_state = False
    while True:
        try:
            user_input = input("Command: ").strip().lower()
            if user_input == "on":
                pump_state = True
                print("💧 [SIM] PUMP ON — irrigation started")
            elif user_input == "off":
                pump_state = False
                print("🛑 [SIM] PUMP OFF — irrigation stopped")
            elif user_input == "q":
                break
            else:
                status = "ON" if pump_state else "OFF"
                print(f"Unknown command. Pump is currently {status}.")
        except KeyboardInterrupt:
            print("\nSimulation stopped.")
            break

if __name__ == "__main__":
    main()
