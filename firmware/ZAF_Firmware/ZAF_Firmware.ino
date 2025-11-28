/**
 * ZAF++ Firmware
 * Platform: Arduino Mega 2560 R3
 * Description: Low-level controller for ZAF++ Automated Feeder & Water Management System.
 * Handles Serial commands from Python backend to control Servo, Pumps, and Relays.
 */

#include <Servo.h>

// --- Pin Definitions ---

// Relays (Active LOW)
const int PIN_RELAY_SERVO_PWR = 22; // Relay Ch 1
const int PIN_RELAY_RUMBLE    = 23; // Relay Ch 2
// Valve Relays 24-27...

// Servo
const int PIN_SERVO_SIG = 9;

// Pumps (L298N)
// Pump 1
const int PIN_PUMP1_PWM = 2;
const int PIN_PUMP1_IN1 = 40;
const int PIN_PUMP1_IN2 = 41;
// Pump 2
const int PIN_PUMP2_PWM = 3;
const int PIN_PUMP2_IN1 = 42;
const int PIN_PUMP2_IN2 = 43;

// --- Constants ---
const int SERVO_HOME_POS = 0;
const int SERVO_DROP_POS = 180; // Adjust as needed for rack travel
const int SERVO_DELAY_MS = 500; // Time for servo to move

Servo foodServo;

// --- Global State ---
String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

void setup() {
  Serial.begin(115200);
  inputString.reserve(200);

  // Initialize Relays
  // Note: Relay Board is Active LOW. HIGH = OFF, LOW = ON.
  // We want them OFF by default.
  pinMode(PIN_RELAY_SERVO_PWR, OUTPUT);
  digitalWrite(PIN_RELAY_SERVO_PWR, HIGH); 

  pinMode(PIN_RELAY_RUMBLE, OUTPUT);
  digitalWrite(PIN_RELAY_RUMBLE, HIGH);

  // Initialize Pump Pins
  pinMode(PIN_PUMP1_PWM, OUTPUT);
  pinMode(PIN_PUMP1_IN1, OUTPUT);
  pinMode(PIN_PUMP1_IN2, OUTPUT);
  
  pinMode(PIN_PUMP2_PWM, OUTPUT);
  pinMode(PIN_PUMP2_IN1, OUTPUT);
  pinMode(PIN_PUMP2_IN2, OUTPUT);

  // Stop pumps initially
  stopPump(1);
  stopPump(2);

  // Attach Servo (but power is off)
  foodServo.attach(PIN_SERVO_SIG);
  
  Serial.println("ZAF++ Firmware Ready");
}

void loop() {
  // Process Serial Commands
  if (stringComplete) {
    parseCommand(inputString);
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void parseCommand(String command) {
  command.trim(); // Remove whitespace/newlines
  
  if (command.startsWith("DISPENSE:")) {
    // Format: DISPENSE:<cycles>
    int separatorIndex = command.indexOf(':');
    if (separatorIndex != -1) {
      int cycles = command.substring(separatorIndex + 1).toInt();
      dispenseFood(cycles);
    }
  } 
  else if (command.startsWith("RUMBLE:")) {
    // Format: RUMBLE:<0/1>
    int separatorIndex = command.indexOf(':');
    if (separatorIndex != -1) {
      int state = command.substring(separatorIndex + 1).toInt();
      setRumble(state);
    }
  }
  else if (command.startsWith("PUMP:")) {
    // Format: PUMP:<id>:<speed>:<dir>
    // id: 1 or 2
    // speed: 0-255
    // dir: 1 (Forward), -1 (Reverse), 0 (Stop)
    int firstColon = command.indexOf(':');
    int secondColon = command.indexOf(':', firstColon + 1);
    int thirdColon = command.indexOf(':', secondColon + 1);
    
    if (firstColon != -1 && secondColon != -1 && thirdColon != -1) {
      int id = command.substring(firstColon + 1, secondColon).toInt();
      int speed = command.substring(secondColon + 1, thirdColon).toInt();
      int dir = command.substring(thirdColon + 1).toInt();
      controlPump(id, speed, dir);
    }
  }
  else if (command == "PING") {
    Serial.println("PONG");
  }
  else {
    Serial.println("ERROR: Unknown Command");
  }
}

// --- Action Functions ---

void dispenseFood(int cycles) {
  Serial.print("DISPENSING: "); Serial.println(cycles);
  
  // 1. Power ON Servo
  digitalWrite(PIN_RELAY_SERVO_PWR, LOW); // Active LOW -> ON
  delay(200); // Wait for power to stabilize

  // 2. Move to Home (ensure starting pos)
  foodServo.write(SERVO_HOME_POS);
  delay(SERVO_DELAY_MS);

  // 3. Cycle
  for (int i = 0; i < cycles; i++) {
    // Move to Drop
    foodServo.write(SERVO_DROP_POS);
    delay(SERVO_DELAY_MS);
    // Move back to Home (Collect)
    foodServo.write(SERVO_HOME_POS);
    delay(SERVO_DELAY_MS);
  }

  // 4. Power OFF Servo
  delay(100);
  digitalWrite(PIN_RELAY_SERVO_PWR, HIGH); // Active LOW -> OFF
  
  Serial.println("DISPENSE_COMPLETE");
}

void setRumble(int state) {
  if (state == 1) {
    digitalWrite(PIN_RELAY_RUMBLE, LOW); // ON
    Serial.println("RUMBLE_ON");
  } else {
    digitalWrite(PIN_RELAY_RUMBLE, HIGH); // OFF
    Serial.println("RUMBLE_OFF");
  }
}

void controlPump(int id, int speed, int dir) {
  int pinPWM, pinIN1, pinIN2;
  
  if (id == 1) {
    pinPWM = PIN_PUMP1_PWM;
    pinIN1 = PIN_PUMP1_IN1;
    pinIN2 = PIN_PUMP1_IN2;
  } else if (id == 2) {
    pinPWM = PIN_PUMP2_PWM;
    pinIN1 = PIN_PUMP2_IN1;
    pinIN2 = PIN_PUMP2_IN2;
  } else {
    Serial.println("ERROR: Invalid Pump ID");
    return;
  }

  if (dir == 0) {
    stopPump(id);
    Serial.print("PUMP_STOPPED:"); Serial.println(id);
  } else {
    // Set Direction
    if (dir == 1) {
      digitalWrite(pinIN1, HIGH);
      digitalWrite(pinIN2, LOW);
    } else {
      digitalWrite(pinIN1, LOW);
      digitalWrite(pinIN2, HIGH);
    }
    // Set Speed
    analogWrite(pinPWM, speed);
    Serial.print("PUMP_RUNNING:"); Serial.println(id);
  }
}

void stopPump(int id) {
  if (id == 1) {
    digitalWrite(PIN_PUMP1_IN1, LOW);
    digitalWrite(PIN_PUMP1_IN2, LOW);
    analogWrite(PIN_PUMP1_PWM, 0);
  } else if (id == 2) {
    digitalWrite(PIN_PUMP2_IN1, LOW);
    digitalWrite(PIN_PUMP2_IN2, LOW);
    analogWrite(PIN_PUMP2_PWM, 0);
  }
}
