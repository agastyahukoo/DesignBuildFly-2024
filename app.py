import time
import threading
import serial  # pyserial
from flask import Flask, render_template
from flask_socketio import SocketIO

# ------------------------------
# Configuration
# ------------------------------
SERIAL_PORT = '/dev/ttyACM0'  # Change to the serial/radio port of your device
BAUD_RATE   = 230400
UPDATE_HZ   = 50              # Adjust how many times per second we emit data

# Shared data structure for YPR
latest_data = {
    'yaw': 0.0,
    'pitch': 0.0,
    'roll': 0.0,
    'looptimer': 0
}

# ------------------------------
# Flask + SocketIO
# ------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'REPLACE_THIS_SECRET'
socketio = SocketIO(app)  # By default, this uses Eventlet for async WS

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected via WebSocket.")

def serial_thread():
    """
    Continuously read IMU lines from the serial device:
        "yaw, pitch, roll, looptimer"
    Update 'latest_data' and emit via SocketIO.
    """
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[INFO] Serial port opened: {SERIAL_PORT} at {BAUD_RATE} baud.")
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port: {e}")
        return

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue

        parts = line.split(',')
        # Expecting 4 parts: yaw, pitch, roll, looptimer
        if len(parts) >= 4:
            try:
                yaw_str, pitch_str, roll_str, loop_str = [p.strip() for p in parts[:4]]
                y = float(yaw_str)
                p = float(pitch_str)
                r = float(roll_str)
                l = float(loop_str)

                latest_data['yaw'] = y
                latest_data['pitch'] = p
                latest_data['roll'] = r
                latest_data['looptimer'] = l

                # Broadcast to all connected clients
                socketio.emit('imu_data', latest_data)

            except ValueError:
                pass  # Could not parse float

        time.sleep(1.0 / UPDATE_HZ)

if __name__ == '__main__':
    # Spawn the background thread
    t = threading.Thread(target=serial_thread, daemon=True)
    t.start()

    # Run Flask + SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)
