import time
import threading
import serial
from flask import Flask, render_template
from flask_socketio import SocketIO

# ========================
# Configuration
# Adjust these values as needed.
# ========================
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 230400
UPDATE_HZ = 50

app = Flask(__name__)
app.config['SECRET_KEY'] = 'REPLACE_THIS_SECRET'
socketio = SocketIO(app)

latest_data = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0, 'looptimer': 0}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('terminal_command')
def handle_terminal_command(cmd):
    socketio.emit('terminal_output', f"You typed: {cmd}")

def serial_thread():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except serial.SerialException:
        return
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue
        parts = line.split(',')
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
                socketio.emit('imu_data', latest_data)
            except ValueError:
                pass
        time.sleep(1.0 / UPDATE_HZ)

if __name__ == '__main__':
    t = threading.Thread(target=serial_thread, daemon=True)
    t.start()
    socketio.run(app, host='0.0.0.0', port=5000)
