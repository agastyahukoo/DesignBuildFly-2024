from flask import Flask, render_template, jsonify, request
import serial
import serial.tools.list_ports
import threading
import os

app = Flask(__name__, template_folder=os.path.abspath(os.path.dirname(__file__)))

# Global variables for aircraft attitude
yaw = 0.0
pitch = 0.0
roll = 0.0

# Default Serial Port Configuration
default_port = "COM5"
default_baud = 230400
SERIAL_PORT = default_port
BAUD_RATE = default_baud
ser = None
connected = False  # Track if serial is connected

def list_serial_ports():
    """
    Returns a list of available serial port devices.
    """
    return [port.device for port in serial.tools.list_ports.comports()]

def connect_serial(port, baud_rate):
    """
    Attempts to open a serial connection with the specified port and baud rate.
    Closes any existing connection beforehand.
    """
    global ser, connected
    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(port, baud_rate, timeout=1)
        connected = True
        return True
    except serial.SerialException as e:
        print(f"Failed to connect to {port}: {e}")
        connected = False
        return False

def read_serial():
    """
    Continuously reads from the serial port to update
    yaw, pitch, and roll in real-time.
    """
    global yaw, pitch, roll, ser
    while True:
        if ser and ser.is_open:
            try:
                line = ser.readline().decode("utf-8").strip()
                if line:
                    values = line.split(", ")
                    if len(values) == 4:
                        yaw, pitch, roll = map(float, values[:3])
            except serial.SerialException as e:
                print("Serial error:", e)
                ser.close()
                break
            except Exception as e:
                print("Error reading serial data:", e)

@app.route('/')
def index():
    """
    Renders the front-end PFD page.
    """
    return render_template('index.html')

@app.route('/get_attitude')
def get_attitude():
    """
    Returns the latest yaw, pitch, and roll values in JSON format.
    """
    return jsonify({"yaw": yaw, "pitch": pitch, "roll": roll})

@app.route('/list_ports')
def get_ports():
    """
    Returns the list of available serial ports in JSON format.
    """
    return jsonify({"ports": list_serial_ports()})

@app.route('/set_serial', methods=['POST'])
def set_serial():
    """
    Sets the serial port and baud rate, then connects.
    Spawns a reading thread to continuously capture attitude data if successful.
    """
    global SERIAL_PORT, BAUD_RATE
    data = request.json
    SERIAL_PORT = data.get("port", default_port)
    BAUD_RATE = int(data.get("baud_rate", default_baud))
    success = connect_serial(SERIAL_PORT, BAUD_RATE)
    if success:
        # Start a thread to read the serial data if not already started
        threading.Thread(target=read_serial, daemon=True).start()
    return jsonify({"success": success})

@app.route('/run_command', methods=['POST'])
def run_command():
    """
    Receives a command from the front-end terminal, parses it,
    executes relevant actions, and returns an appropriate response.
    """
    data = request.json
    user_command = data.get("command", "").strip()
    response = parse_command(user_command)
    return jsonify({"response": response})

def parse_command(cmd):
    """
    Parses the command entered in the terminal and returns a string response.
    You can customize or extend these commands to fit your system.
    """
    global SERIAL_PORT, BAUD_RATE, connected, yaw, pitch, roll
    
    if not cmd:
        return ""
    
    parts = cmd.split()
    command = parts[0].lower()
    args = parts[1:]  # Any additional arguments after the command

    if command == "help":
        return (
            "Available Commands:\n"
            "help                     - Show this help message\n"
            "clear                    - Clear the terminal\n"
            "listports                - List available serial ports\n"
            "setport <port>           - Set the current serial port\n"
            "setbaud <rate>           - Set the current baud rate\n"
            "connect                  - Connect using current port and baud\n"
            "status                   - Show current connection status\n"
            "getattitude              - Show current yaw, pitch, roll\n"
            "exit                     - Disconnect (if connected)\n"
        )
    
    elif command in ["clear", "cls"]:
        # Actual clearing can happen on the front-end; we can return a note
        return "Terminal cleared."
    
    elif command == "listports":
        ports = list_serial_ports()
        if ports:
            return "Available Ports:\n" + "\n".join(ports)
        else:
            return "No ports found."
    
    elif command == "setport":
        if not args:
            return "Usage: setport <port>"
        SERIAL_PORT = args[0]
        return f"Serial port set to {SERIAL_PORT}"
    
    elif command == "setbaud":
        if not args:
            return "Usage: setbaud <baud_rate>"
        try:
            BAUD_RATE = int(args[0])
            return f"Baud rate set to {BAUD_RATE}"
        except ValueError:
            return "Invalid baud rate. Usage: setbaud <baud_rate>"
    
    elif command == "connect":
        success = connect_serial(SERIAL_PORT, BAUD_RATE)
        if success:
            # Start reading thread if not already started
            threading.Thread(target=read_serial, daemon=True).start()
            return f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud."
        else:
            return f"Failed to connect to {SERIAL_PORT} at {BAUD_RATE} baud."
    
    elif command == "status":
        status_msg = (
            f"Port: {SERIAL_PORT}\n"
            f"Baud: {BAUD_RATE}\n"
            f"Connected: {'Yes' if connected else 'No'}\n"
        )
        return status_msg
    
    elif command == "getattitude":
        return f"Yaw: {yaw}, Pitch: {pitch}, Roll: {roll}"
    
    elif command in ["exit", "quit"]:
        if ser and ser.is_open:
            ser.close()
        connected = False
        return "Disconnected from serial (if connected)."
    
    else:
        return f"Unknown command: {command}. Type 'help' for a list of commands."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
