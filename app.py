from flask import Flask, render_template, jsonify
import serial
import threading
import os

app = Flask(__name__, template_folder=os.path.abspath(os.path.dirname(__file__)))

# Serial port configuration (Update the port as needed)
SERIAL_PORT = "/dev/ttyUSB0"  # Change based on your system
BAUD_RATE = 230400

# Global variables for aircraft attitude
yaw, pitch, roll = 0.0, 0.0, 0.0

def read_serial():
    global yaw, pitch, roll
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    while True:
        try:
            line = ser.readline().decode("utf-8").strip()
            if line:
                values = line.split(", ")
                if len(values) == 4:
                    yaw, pitch, roll = map(float, values[:3])
        except Exception as e:
            print("Error reading serial data:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_attitude')
def get_attitude():
    return jsonify({"yaw": yaw, "pitch": pitch, "roll": roll})

if __name__ == '__main__':
    # Start serial reading in a separate thread
    serial_thread = threading.Thread(target=read_serial, daemon=True)
    serial_thread.start()
    app.run(host='0.0.0.0', port=4000, debug=True)
