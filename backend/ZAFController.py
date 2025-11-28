import serial
import time
import logging
from typing import Optional

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ZAFController")

class ZAFController:
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = 115200, timeout: int = 2):
        """
        Initialize the ZAF Controller.
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyACM0' or 'COM3').
            baudrate (int): Baud rate (default 115200).
            timeout (int): Read timeout in seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.connected = False

    def connect(self):
        """Establish serial connection to the Arduino."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Wait for Arduino reset
            self.connected = True
            logger.info(f"Connected to ZAF++ Controller on {self.port}")
            
            # Clear buffer
            self.ser.reset_input_buffer()
            
            # Handshake
            response = self.send_command("PING")
            if "PONG" in response:
                logger.info("Handshake successful.")
            else:
                logger.warning(f"Handshake failed. Response: {response}")
                
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            self.connected = False

    def disconnect(self):
        """Close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            logger.info("Disconnected from ZAF++ Controller")

    def send_command(self, command: str) -> str:
        """
        Send a command to the Arduino and wait for a response.
        
        Args:
            command (str): The command string (e.g., "DISPENSE:1").
            
        Returns:
            str: The response from the Arduino.
        """
        if not self.connected or not self.ser:
            logger.error("Not connected to controller.")
            return ""

        try:
            full_command = f"{command}\n"
            self.ser.write(full_command.encode('utf-8'))
            logger.debug(f"Sent: {command}")
            
            # Read response
            response = self.ser.readline().decode('utf-8').strip()
            logger.debug(f"Received: {response}")
            return response
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return ""

    def dispense_food(self, cycles: int = 1):
        """
        Dispense food by cycling the servo.
        
        Args:
            cycles (int): Number of dispense cycles.
        """
        logger.info(f"Dispensing food: {cycles} cycles")
        
        # Optional: Turn on rumble pack briefly before/during?
        # For now, just dispense as per firmware logic.
        response = self.send_command(f"DISPENSE:{cycles}")
        
        # Wait for completion if needed (firmware sends DISPENSE_COMPLETE)
        # The simple send_command reads one line. 
        # Dispense might take time and send multiple lines (DISPENSING..., DISPENSE_COMPLETE).
        # We might need a read loop here if we want to block until finished.
        if "DISPENSING" in response:
            # Wait for the completion message
            while True:
                line = self.ser.readline().decode('utf-8').strip()
                if line == "DISPENSE_COMPLETE":
                    logger.info("Dispense cycle completed successfully.")
                    break
                elif line:
                    logger.debug(f"Dispense status: {line}")
                else:
                    # Timeout
                    logger.warning("Timeout waiting for dispense completion.")
                    break

    def set_rumble_pack(self, state: bool):
        """
        Control the fluidization rumble motor.
        
        Args:
            state (bool): True for ON, False for OFF.
        """
        val = 1 if state else 0
        logger.info(f"Setting Rumble Pack: {'ON' if state else 'OFF'}")
        self.send_command(f"RUMBLE:{val}")

    def control_pump(self, pump_id: int, speed: int, direction: int):
        """
        Control a water pump.
        
        Args:
            pump_id (int): Pump ID (1 or 2).
            speed (int): PWM speed (0-255).
            direction (int): 1 (Forward), -1 (Reverse), 0 (Stop).
        """
        logger.info(f"Controlling Pump {pump_id}: Speed={speed}, Dir={direction}")
        self.send_command(f"PUMP:{pump_id}:{speed}:{direction}")

if __name__ == "__main__":
    # Example Usage
    # Change port to match your system (e.g., 'COM3' on Windows, '/dev/ttyACM0' on Linux)
    PORT = 'COM3' 
    
    zaf = ZAFController(port=PORT)
    zaf.connect()
    
    if zaf.connected:
        try:
            # Test Rumble
            zaf.set_rumble_pack(True)
            time.sleep(1)
            zaf.set_rumble_pack(False)
            
            # Test Dispense
            zaf.dispense_food(1)
            
            # Test Pump
            zaf.control_pump(1, 150, 1) # Pump 1, Speed 150, Fwd
            time.sleep(2)
            zaf.control_pump(1, 0, 0)   # Stop
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            zaf.disconnect()
