# ZAF++ Hardware Wiring Map

**Version:** 1.0
**Controller:** Arduino Mega 2560 R3
**Power Source:** 12V DC PSU

---

## 1. Power Distribution Architecture

| Source Voltage | Target Component      | Regulation Method        | Control / Gating                  |
| :------------- | :-------------------- | :----------------------- | :-------------------------------- |
| **12V DC**     | Water Pumps (L298N)   | Direct                   | L298N Driver (PWM)                |
| **12V DC**     | Solenoid Valves       | Direct                   | Relay Board (Active LOW)          |
| **12V DC**     | **Servo Power (6V)**  | Buck Converter (12V->6V) | **Relay Ch 1** (Switches 6V Line) |
| **12V DC**     | **Rumble Motor (5V)** | Buck Converter (12V->5V) | **Relay Ch 2** (Switches 5V Line) |

> **[!IMPORTANT]**
> The **Servo Power** must be routed through a Relay. The Arduino controls the Relay to cut power to the servo when not in use to prevent jitter and overheating.

---

## 2. Arduino Mega 2560 Pinout

### A. 16-Channel Relay Module (Digital 22-37)

_Active LOW Logic_

| Arduino Pin | Relay Channel | Function         | Description                    |
| :---------- | :------------ | :--------------- | :----------------------------- |
| **D22**     | CH 1          | **Servo Power**  | Gates 6V to Hiwonder Servo     |
| **D23**     | CH 2          | **Rumble Motor** | Gates 5V to Rumble Motor       |
| **D24**     | CH 3          | Valve 1          | Solenoid Valve Control         |
| **D25**     | CH 4          | Valve 2          | Solenoid Valve Control         |
| **D26**     | CH 5          | Valve 3          | Solenoid Valve Control         |
| **D27**     | CH 6          | Valve 4          | Solenoid Valve Control         |
| **D28-D37** | CH 7-16       | _Auxiliary_      | Spares for Lights/Heaters/etc. |

### B. Water Pumps - L298N Drivers (PWM 2-7)

_L298N Logic: ENA (Speed/PWM), IN1/IN2 (Direction)_

| Component  | Signal      | Arduino Pin | Connection on L298N |
| :--------- | :---------- | :---------- | :------------------ |
| **Pump 1** | Speed (PWM) | **D2**      | ENA                 |
|            | Direction A | **D40**     | IN1                 |
|            | Direction B | **D41**     | IN2                 |
| **Pump 2** | Speed (PWM) | **D3**      | ENB                 |
|            | Direction A | **D42**     | IN3                 |
|            | Direction B | **D43**     | IN4                 |
| **Pump 3** | Speed (PWM) | **D4**      | ENA (Driver 2)      |
|            | Direction A | **D44**     | IN1 (Driver 2)      |
|            | Direction B | **D45**     | IN2 (Driver 2)      |

_(Note: Pins 40-45 are assigned for Direction control to keep PWM pins 2-7 free for Speed)_

### C. Food Dispenser Servo

| Component      | Signal     | Arduino Pin | Notes                                |
| :------------- | :--------- | :---------- | :----------------------------------- |
| **Servo Data** | PWM Signal | **D9**      | Connects to Orange/White Signal Wire |

---

## 3. Component Wiring Details

### L298N Motor Driver Connections

1.  **12V Input:** Connect directly to 12V PSU.
2.  **GND:** Connect to PSU GND **AND** Arduino GND (Common Ground is critical).
3.  **5V Output:** _Do not use if powering Arduino via USB._

### Relay Board Connections

1.  **VCC:** 5V from Arduino (or separate 5V PSU if current draw is high).
2.  **GND:** Common Ground.
3.  **Inputs 1-16:** Connect to Arduino D22-D37.

### Hiwonder 20kg Servo

1.  **Red (+):** To Relay Ch 1 (NO terminal). _Common terminal of Relay goes to 6V Buck (+)._
2.  **Brown (-):** To Common Ground.
3.  **Orange (Sig):** To Arduino D9.
