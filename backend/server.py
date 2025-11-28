from flask import Flask, jsonify, request
from flask_cors import CORS
# ADAPTATION: Matching your filename 'ZAFController.py'
from ZAFController import ZAFController 
import sys
import platform

# Initialize Flask
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for React

# Initialize Hardware Connection
# Auto-detect port (Linux vs Windows)
port = 'COM3' if platform.system() == 'Windows' else '/dev/ttyACM0'

try:
    zaf = ZAFController(port)
    print(f"System Online: Connected to {port}")
except Exception as e:
    zaf = None
    print(f"Simulation Mode: Could not connect to hardware ({e})")

@app.route('/api/status', methods=['GET'])
def get_status():
    # In a real scenario, we would query the Arduino for status
    return jsonify({"status": "online", "hardware": "connected" if zaf else "simulated"})

@app.route('/api/feed', methods=['POST'])
def feed():
    if not zaf: return jsonify({"error": "Hardware offline"}), 503
    
    data = request.json
    cycles = data.get('cycles', 1)
    resp = zaf.dispense(cycles)
    return jsonify({"action": "feed", "response": resp})

@app.route('/api/rumble', methods=['POST'])
def rumble():
    if not zaf: return jsonify({"error": "Hardware offline"}), 503
    
    data = request.json
    state = data.get('state', 0)
    resp = zaf.rumble(state)
    return jsonify({"action": "rumble", "state": state, "response": resp})

if __name__ == '__main__':
    # Run the web server on all interfaces (so you can see it from Windows)
    app.run(host='0.0.0.0', port=5000, debug=True)
