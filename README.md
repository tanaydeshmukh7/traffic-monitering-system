# AI Traffic Monitoring System

This project is an AI-powered Traffic Monitoring System that uses YOLOv11 for vehicle detection and tracking. It integrates with an Arduino Uno to control traffic lights (LEDs) and a buzzer to alert for traffic violations (e.g., crossing a red light). It also features a traffic dashboard for monitoring the state of the traffic.

## Features
- **Vehicle Detection & Tracking:** Uses YOLOv11 to detect and track vehicles (cars, motorcycles, buses, trucks).
- **Virtual Stop Line:** Monitors a virtual stop line on the camera feed.
- **Red Light Violation Detection:** Detects if a vehicle crosses the virtual stop line when the signal is RED.
- **Hardware Integration:** Communicates with an Arduino to control traffic signals (Red, Yellow, Green LEDs) and triggers a buzzer upon violation.
- **Traffic Density Monitoring:** Classifies traffic density as LOW, MEDIUM, or HIGH based on the number of vehicles passing in a given time window.
- **Evidence Capture:** Saves snapshot images of vehicles that commit violations.

## Prerequisites

### Hardware Requirements
- Arduino Uno
- 3 LEDs (Red, Yellow, Green)
- 1 Active Buzzer
- 4 Resistors (220 ohm or 330 ohm) for LEDs
- Jumper wires
- Breadboard
- USB Cable to connect Arduino to the computer
- Webcam or Laptop Camera (Index 0)

### Software Requirements
- Python 3.8+
- Arduino IDE
- Git

## Hardware Setup (Arduino)

### Wiring Guide
Connect the components to your Arduino Uno as follows (you can adjust the pins in your Arduino code if needed):

1. **Red LED:** 
   - Anode (long leg) -> 220Ω Resistor -> Arduino Digital Pin 4
   - Cathode (short leg) -> GND
2. **Yellow LED:** 
   - Anode (long leg) -> 220Ω Resistor -> Arduino Digital Pin 3
   - Cathode (short leg) -> GND
3. **Green LED:** 
   - Anode (long leg) -> 220Ω Resistor -> Arduino Digital Pin 2
   - Cathode (short leg) -> GND
4. **Buzzer:** 
   - Positive pin (+) -> Arduino Digital Pin 5
   - Negative pin (-) -> GND

### Arduino Sketch
You need an Arduino sketch that reads serial commands and controls the LEDs and buzzer accordingly. The Python script sends the following commands over serial:
- `SIGNAL_RED`
- `SIGNAL_YELLOW`
- `SIGNAL_GREEN`
- `EVENT` (Trigger buzzer for violation)
- `LOW`, `MEDIUM`, `HIGH` (For density, can be used to control other indicators)

*(Make sure to upload a sketch to your Arduino that listens to these commands on a baud rate of 9600).*

### COM Port Configuration
By default, the Python script is configured to communicate with the Arduino on `COM15`. 
- Open the Arduino IDE, go to **Tools > Port** to find out which COM port your Arduino is connected to.
- If it's different from `COM15`, open `traffic dashboard/main.py` and `arduino_test.py` and change the `ARDUINO_PORT` variable to match your port (e.g., `COM3`).

## Software Setup (Python)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tanaydeshmukh7/traffic-monitering-system.git
   cd traffic-monitering-system
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure `ultralytics`, `opencv-python`, `pyserial`, and other required libraries are installed).*

4. **Verify Arduino Connection:**
   You can run the test script to manually test if the LEDs and buzzer are responding correctly.
   ```bash
   python arduino_test.py
   ```

## Running the System

To start the AI Traffic Monitoring System:

1. Navigate to the `traffic dashboard` folder:
   ```bash
   cd "traffic dashboard"
   ```

2. Run the main monitoring script:
   ```bash
   python main.py
   ```

3. A window will open showing the camera feed. Vehicles crossing the virtual stop line while the system is in "RED" mode will trigger a buzzer on the Arduino, and an image of the violation will be saved in the `captured_vehicles/` directory.

4. To stop the system, press **`q`** on your keyboard while focusing on the video window.

## Project Structure
- `arduino_test.py`: A simple CLI script to test the Arduino connection and components.
- `traffic dashboard/main.py`: The core AI script that captures video, runs YOLOv11 tracking, and sends commands to the Arduino.
- `traffic dashboard/app.py`: Web dashboard application.
- `yolo11n.pt`: The pre-trained YOLOv11 model weights.
- `captured_vehicles/`: Directory where images of traffic violations are saved.
