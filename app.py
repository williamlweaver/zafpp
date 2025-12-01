import sys
import os
import logging
from flask import Flask, render_template, jsonify, request

# Ensure backend imports work
sys.path.append(os.getcwd())
from backend.ZAFController import ZAFController

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZAF_WebApp")

app = Flask(__name__)

# Initialize Hardware
PORT = '/dev/ttyACM0' # Default for Linux
zaf = None

try:
    logger.info(f"Attempting to connect to hardware on {PORT}...")
    zaf = ZAFController(port=PORT)
    zaf.connect()
    if zaf.connected:
        logger.info("Hardware Connected Successfully.")
    else:
        logger.warning("Hardware Connection Failed. Running in Simulation Mode.")
except Exception as e:
    logger.error(f"Error initializing hardware: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    state = "ONLINE" if zaf and zaf.connected else "OFFLINE"
    return jsonify({
        "status": state,
        "last_feed": "Unknown" # Placeholder for now
    })

@app.route('/feed', methods=['POST'])
def feed():
    if zaf and zaf.connected:
        try:
            zaf.dispense_food(1)
            return jsonify({"status": "success", "message": "Feeding initiated"})
        except Exception as e:
            logger.error(f"Feeding error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        logger.info("Simulation: Feeding triggered (Hardware Offline)")
        return jsonify({"status": "simulated", "message": "Feeding simulated (Hardware Offline)"})

if __name__ == '__main__':
    # Run on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
