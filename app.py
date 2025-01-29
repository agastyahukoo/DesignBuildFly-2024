from flask import Flask, render_template, jsonify, request
import serial
import serial.tools.list_ports
import threading
import os

app = Flask(__name__, template_folder=os.path.abspath(os.path.dirname(__file__)))

# Default Serial Port Configuration
default_port = "COM5"
default_baud = 230400
SERIAL_PORT = default_port
BAUD_RATE = default_baud
ser = None

def list_serial_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def connect_serial(port, baud_rate):
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(port, baud_rate, timeout=1)
        return True
    except serial.SerialException as e:
        print(f"Failed to connect to {port}: {e}")
        return False

def read_serial():
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
    return render_template('index.html')

@app.route('/get_attitude')
def get_attitude():
    return jsonify({"yaw": yaw, "pitch": pitch, "roll": roll})

@app.route('/list_ports')
def get_ports():
    return jsonify({"ports": list_serial_ports()})

@app.route('/set_serial', methods=['POST'])
def set_serial():
    global SERIAL_PORT, BAUD_RATE
    data = request.json
    SERIAL_PORT = data.get("port", default_port)
    BAUD_RATE = int(data.get("baud_rate", default_baud))
    success = connect_serial(SERIAL_PORT, BAUD_RATE)
    if success:
        threading.Thread(target=read_serial, daemon=True).start()
    return jsonify({"success": success})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
