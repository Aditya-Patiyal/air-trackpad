# Air Trackpad 🖐️💻

Air Trackpad is a computer vision–based gesture control system that transforms hand gestures into trackpad-like actions such as cursor movement, clicking, scrolling, zooming, and drag-and-drop using a standard webcam. It enables completely touchless interaction without any external hardware.

---

## 🚀 Features & Gesture Controls

### 🖱️ Cursor Movement
- The system tracks the position of the user’s index finger in real time.
- Cursor movement is mapped proportionally to finger motion.
- Smoothing techniques are applied to reduce jitter and improve stability.

**Gesture:**  
👉 Move index finger in the air to control the cursor.

---

### 👆 Click (Visual Feedback Enabled)
- A left click is triggered when the distance between the **thumb and index finger** falls below a defined threshold.
- A **full green circle** appears on the screen to visually confirm the click action.

**Gesture:**  
🤏 Bring thumb and index finger together.

**Visual Indicator:**  
🟢 Green circle → Click detected

---

### 📜 Scrolling (Visual Feedback Enabled)
- Scrolling is controlled using two fingers (index and middle finger).
- Vertical finger movement is translated into scroll up/down actions.
- A **blue circular indicator** appears while scrolling is active.

**Gesture:**  
✌️ Move index + middle finger up/down.

**Visual Indicator:**  
🔵 Blue circle → Scrolling active

---

### 🔍 Zoom In / Zoom Out
- Zooming is controlled using the **left hand’s vertical movement**.
- Moving the left hand **upwards** triggers zoom in.
- Moving the left hand **downwards** triggers zoom out.
- This allows intuitive zoom control similar to touch-based pinch gestures.

**Gesture:**  
✋ Left hand up → Zoom In  
✋ Left hand down → Zoom Out

---

### ✋ Drag and Drop
- Drag mode is activated by holding the pinch gesture (thumb + index finger).
- While the pinch is held, cursor movement drags the selected object.
- Releasing the pinch drops the object at the target location.

**Gesture:**  
🤏 Hold pinch → move → release

---

### ⚡ Real-Time Performance
- Built using MediaPipe hand landmarks for accurate detection.
- Optimized for low-latency, real-time interaction.

---

## 🛠 Tech Stack
- **Python**
- **OpenCV** – video capture, rendering, and visual feedback
- **MediaPipe** – real-time hand landmark detection

---

## ▶️ How to Run

1. Clone the repository:
```bash
git clone https://github.com/Aditya-Patiyal/air-trackpad.git
cd air-trackpad
