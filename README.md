# Zebrafish Automated Feeder Plus Plus (ZAF++) - SAIL Lab Instrument Control

# ⚠️ MOVED TO GITLAB ⚠️

**As of December 2, 2025, this repository has migrated.**

Future development for the ZAF++ project (SAIL Team) is continuing at our new home:
👉 **[https://gitlab.com/umes-sail/zafpp](https://gitlab.com/umes-sail/zafpp)**

Please update your bookmarks and clones. The code in this repository is now archived and will not receive updates.

---

## System Architecture

The ZAF++ system is designed as a modular instrument for automated zebrafish husbandry.

*   **Host**: Debian NUC 14 Pro (running X11). Acts as the central brain and user interface.
*   **Interface**: 7-inch Touchscreen running a Flask Web Application (optimized for 1024x600 resolution).
*   **Controller**: Arduino MEGA 2560 R3 (connected via USB/Serial). Handles real-time hardware control (motors, relays, sensors).

## Installation Guide

Follow these steps to deploy the software on a new Linux host (e.g., Debian/Ubuntu).

### 1. Clone the Repository
```bash
git clone https://github.com/williamlweaver/zafpp.git
cd zafpp
```

### 2. Set Up Python Environment
Create and activate a virtual environment to manage dependencies.
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Hardware Permissions
Grant the user permission to access the serial port (USB).
```bash
sudo usermod -a -G dialout $USER
# You must logout and login again for this to take effect.
```

## Hardware Map

Summary of key connections between the Arduino MEGA and the ZAF++ hardware.

| Component | Arduino Pin | Description |
| :--- | :--- | :--- |
| **Servo Data** | **D9** | Control signal for Food Dispenser Servo |
| **Servo Power** | **D22** (Relay Ch 1) | Gates 6V power to Servo (Active LOW) |
| **Rumble Motor** | **D23** (Relay Ch 2) | Gates 5V power to Rumble Motor |
| **Pump 1 (Speed)** | **D2** (PWM) | L298N ENA |
| **Pump 1 (Dir)** | **D40, D41** | L298N IN1, IN2 |
| **Pump 2 (Speed)** | **D3** (PWM) | L298N ENB |
| **Pump 2 (Dir)** | **D42, D43** | L298N IN3, IN4 |

## Startup Logic

The system is designed to auto-start on boot using the `start_instrument.sh` script.

### `start_instrument.sh`
This script performs the following:
1.  Navigates to the project directory.
2.  Activates the Python virtual environment.
3.  Launches the Flask Web Interface (`app.py`).

**To run manually:**
```bash
./start_instrument.sh
```

*Note: For a full kiosk experience, configure your Window Manager (e.g., Openbox/i3) to launch Chromium in kiosk mode pointing to `http://localhost:5000` after this script starts.*

## Safety Features

*   **Software Lockout**: The "FEED NOW" button includes a mandatory **5-second cooldown** period. This prevents accidental double-feeding or rapid-fire activation that could stress the fish or jam the mechanism.
*   **Servo Power Gating**: The firmware automatically cuts power to the servo (via Relay Ch 1) when not in use to prevent jitter, overheating, and noise.
