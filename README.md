This project simulates real-time human arm movements using IMU (Inertial Measurement Unit) and EMG (Electromyography) data to control a digital robotic arm in Unity. Designed as a gesture-driven interactive game, the system maps user arm motions to digital counterparts for a responsive gaming experience.

🎯 Objective
Build an interactive game where a digital robot arm simulates a player's real arm movements in real time, powered by data from IMU and EMG sensors mounted on a wearable sleeve.

🧩 System Components
IMU Sensor (e.g., MPU6050 or similar): Captures orientation data (quaternions & acceleration)

EMG Sensor: Reads muscle activation using 6 electrodes across 2 muscles

Python App: For data collection, analysis, training, and communication with Unity

Unity Game: Visualizes the robot arm and provides interactive gameplay

Blender Model: 3D robotic arm model for realistic joint movement

💻 Software Requirements
1. Python (≥ 3.12)
Install from: https://www.python.org/

Install required packages:
pip install matplotlib numpy pyserial pillow
2. Unity Engine
Download from: https://unity.com/download
Use Unity Hub to manage versions and import the project.

3. Blender (if editing 3D model)
Download from: https://www.blender.org/download/

🧤 Wearable Sleeve Setup
IMU Sensor
Attach to the front-center of the wrist.

Measures orientation using quaternion output.

EMG Sensor
6 electrodes across 2 muscles.

Used for gesture classification (e.g., hand open / close).

🎮 Game Instructions
Launch the Python program (Window2.py)

Click Start → enters training phase.

Click Hand Open and Hand Close to collect labeled EMG data.

Data is processed and predictions visualized.

Click Disconnect to finish training.

Launch Unity game → Click Game Start

The robotic arm will now respond to IMU & EMG data in real time.

Game Rules:
On the virtual table, three moving balls appear.

Only one is the "correct" ball.

Pick the correct ball and place it in the basket.

The player who scores the most balls in limited time wins.
