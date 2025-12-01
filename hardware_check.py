import time
import logging
import sys
import os

# Add the current directory to sys.path to ensure backend imports work
sys.path.append(os.getcwd())

from backend.ZAFController import ZAFController

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HardwareCheck")

# Hardware Mapping from docs/hardware_wiring_map.md
HARDWARE_MAP = {
    "Servo Power Relay": {"pin": 22, "type": "relay_unsupported", "desc": "Gates 6V to Servo"},
    "Rumble Motor":      {"pin": 23, "type": "rumble",           "desc": "Gates 5V to Rumble Motor"},
    "Valve 1":           {"pin": 24, "type": "relay_unsupported", "desc": "Solenoid Valve Control"},
    "Valve 2":           {"pin": 25, "type": "relay_unsupported", "desc": "Solenoid Valve Control"},
    "Valve 3":           {"pin": 26, "type": "relay_unsupported", "desc": "Solenoid Valve Control"},
    "Valve 4":           {"pin": 27, "type": "relay_unsupported", "desc": "Solenoid Valve Control"},
    "Pump 1":            {"pin": 2,  "type": "pump",             "id": 1, "desc": "Water Pump 1"},
    "Pump 2":            {"pin": 3,  "type": "pump",             "id": 2, "desc": "Water Pump 2"},
    # Pump 3 is listed in docs but firmware only seems to support 2 pumps in controlPump function?
    # Checking firmware again: controlPump only handles id 1 and 2.
    # "Pump 3":            {"pin": 4,  "type": "pump_unsupported", "id": 3, "desc": "Water Pump 3"},
}

def test_hardware():
    # Initialize Controller
    # Note: Port may need to be adjusted by the user.
    # We'll try a common default or let the user specify.
    port = '/dev/ttyACM0' 
    if len(sys.argv) > 1:
        port = sys.argv[1]
        
    logger.info(f"Initializing ZAFController on {port}...")
    zaf = ZAFController(port=port)
    
    try:
        zaf.connect()
        if not zaf.connected:
            logger.error("Failed to connect to controller. Check connection and port.")
            return

        logger.info("Starting Hardware Check Sequence...")
        time.sleep(1)

        for name, config in HARDWARE_MAP.items():
            logger.info(f"--- Testing {name} ({config['desc']}) ---")
            
            device_type = config.get("type")
            
            if device_type == "rumble":
                logger.info(f"Turning ON {name}...")
                zaf.set_rumble_pack(True)
                time.sleep(2)
                logger.info(f"Turning OFF {name}...")
                zaf.set_rumble_pack(False)
                
            elif device_type == "pump":
                pump_id = config.get("id")
                logger.info(f"Running {name} (ID: {pump_id}) Forward at Speed 150...")
                zaf.control_pump(pump_id, 150, 1)
                time.sleep(2)
                logger.info(f"Stopping {name}...")
                zaf.control_pump(pump_id, 0, 0)
                
            elif device_type == "relay_unsupported":
                logger.warning(f"SKIPPING {name}: Control not supported by current firmware.")
                
            elif device_type == "pump_unsupported":
                logger.warning(f"SKIPPING {name}: Pump ID not supported by current firmware.")
                
            else:
                logger.warning(f"Unknown device type for {name}")
            
            time.sleep(0.5)

        logger.info("Hardware Check Complete.")

    except KeyboardInterrupt:
        logger.info("Hardware check interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Cleaning up...")
        zaf.disconnect()

if __name__ == "__main__":
    test_hardware()
