Air Trackpad – Vision-Based Cursor Control System

This project implements a vision-based mid-air cursor control system using real-time hand tracking as an alternative to traditional input devices. The system supports smooth cursor movement with configurable dead zones, acceleration, and motion smoothing to reduce jitter and fatigue. Single-click interaction is implemented using dwell-based confirmation with visual feedback, allowing reliable selection without physical buttons. Two-finger scrolling is supported with velocity smoothing and inertia, enabling controlled and natural scrolling behavior, while zoom control is handled through vertical hand motion with dwell-based intent detection and throttling to prevent accidental zooming. The interaction design prioritizes stability and predictability, allowing the system to be used for extended periods rather than short demonstrations. Mode separation between cursor movement, scrolling, and zooming ensures that gestures do not interfere with each other, reducing accidental input and improving overall usability.

Development and Design Process

The project was developed through iterative prototyping and hands-on testing, with a strong focus on identifying and resolving real usability issues rather than maximizing feature count. Multiple gesture-based approaches, including pinch-based clicking, posture-based activation, and double-click emulation, were implemented and deliberately removed after testing revealed problems such as cursor instability, unintended actions, user fatigue, and conflicts with operating system behavior. Parameters such as smoothing, dwell timing, dead zones, and inertia were repeatedly tuned based on observed behavior. The final system reflects conscious design trade-offs, emphasizing interaction reliability and user experience while acknowledging the practical limitations of mid-air human–computer interaction.

How to Run
	1.	Clone the repository and navigate to the project directory.
	2.	Create and activate a Python virtual environment.
	3.	Install the required dependencies (OpenCV, MediaPipe, PyAutoGUI).
	4.	Run the main script: python hand_detect.py
Press q to exit the application.

Note: The project was tested on macOS. Cursor control permissions may need to be enabled in system accessibility settings for mouse control to function correctly.
