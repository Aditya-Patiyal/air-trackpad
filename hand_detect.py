import pyautogui
pyautogui.FAILSAFE = False
import cv2
import mediapipe as mp
import time

MODE_CURSOR = "cursor"
MODE_SCROLL = "scroll"
MODE_ZOOM = "zoom"

current_mode = MODE_CURSOR

screen_width, screen_height = pyautogui.size()
prev_x, prev_y = 0, 0
smoothening = 5
clicking = False
DEAD_ZONE = 15
frame_margin = 100
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

DWELL_INDICATOR_RADIUS = 30

CLICK_THRESHOLD_CLOSE = 0.03
CLICK_THRESHOLD_OPEN = 0.05
CLICK_COOLDOWN_FRAMES = 10
click_cooldown = 0

DWELL_TIME = 3.0   # seconds (intentional dwell click)
DWELL_RADIUS = 20 # pixels
dwell_start_time = None
last_dwell_x, last_dwell_y = None, None

ACCELERATION_SCALE = 0.15   # controls how aggressive acceleration is

SCROLL_SPEED = 40
scroll_mode = False
prev_scroll_y = None

MAX_SCROLL_STEP = 30        # max scroll per frame
SCROLL_DEAD_ZONE = 8        # ignore tiny movements
SCROLL_INDICATOR_HEIGHT = 60

scroll_velocity = 0.0
SCROLL_SMOOTHING = 0.2   # lower = smoother, higher = more responsive

# ---- ZOOM CONFIG ----
zoom_mode = False
zoom_velocity = 0.0
prev_zoom_y = None
ZOOM_VERTICAL_SCALE = 0.35
ZOOM_DEAD_ZONE = 12   # pixels

# Added zoom dwell config
ZOOM_DWELL_TIME = 0.5   # seconds to confirm zoom intent
zoom_dwell_start = None

# Added scroll inertia config
SCROLL_INERTIA_DECAY = 0.92   # closer to 1 = longer glide
SCROLL_MIN_VELOCITY = 0.5    # below this, stop scrolling

# Added zoom step cooldown config
ZOOM_STEP_INTERVAL = 0.12   # seconds between zoom steps
last_zoom_step_time = 0

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7
)
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)

    if click_cooldown > 0:
        click_cooldown -= 1

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[i].classification[0].label
            is_left_hand = (hand_label == "Left")
            is_right_hand = (hand_label == "Right")

            index_finger_tip = hand_landmarks.landmark[8]

            middle_finger_tip = hand_landmarks.landmark[12]
            index_pip = hand_landmarks.landmark[6]
            middle_pip = hand_landmarks.landmark[10]

            ring_finger_tip = hand_landmarks.landmark[16]
            ring_pip = hand_landmarks.landmark[14]

            two_fingers_up = (
                index_finger_tip.y < index_pip.y and
                middle_finger_tip.y < middle_pip.y
            )

            frame_h, frame_w, _ = frame.shape

            x_cam = int(index_finger_tip.x * frame_w)
            y_cam = int(index_finger_tip.y * frame_h)

            if is_left_hand:
                current_mode = MODE_ZOOM
            elif is_right_hand:
                if two_fingers_up:
                    current_mode = MODE_SCROLL
                else:
                    current_mode = MODE_CURSOR

            if current_mode != MODE_CURSOR:
                dwell_start_time = None
                last_dwell_x, last_dwell_y = None, None

            if current_mode != MODE_SCROLL:
                prev_scroll_y = None
                scroll_velocity = 0.0

            if current_mode != MODE_ZOOM:
                prev_zoom_y = None
                zoom_velocity = 0.0
                zoom_dwell_start = None
                last_zoom_step_time = 0

            x_cam = max(frame_margin, min(x_cam, frame_w - frame_margin))
            y_cam = max(frame_margin, min(y_cam, frame_h - frame_margin))

            screen_x = (x_cam - frame_margin) * screen_width / (frame_w - 2 * frame_margin)
            screen_y = (y_cam - frame_margin) * screen_height / (frame_h - 2 * frame_margin)

            if current_mode == MODE_CURSOR:
                dx = index_finger_tip.x - hand_landmarks.landmark[4].x
                dy = index_finger_tip.y - hand_landmarks.landmark[4].y
                distance = (dx**2 + dy**2) ** 0.5

                if distance < CLICK_THRESHOLD_CLOSE and click_cooldown == 0:
                    if not clicking:
                        pyautogui.click()
                        clicking = True
                        click_cooldown = CLICK_COOLDOWN_FRAMES
                    dwell_start_time = None
                    last_dwell_x, last_dwell_y = None, None
                elif distance > CLICK_THRESHOLD_OPEN:
                    clicking = False

            if current_mode == MODE_ZOOM:
                current_time = time.time()

                if zoom_dwell_start is None:
                    zoom_dwell_start = current_time
                    prev_zoom_y = y_cam
                    zoom_velocity = 0.0

                elapsed_zoom_dwell = current_time - zoom_dwell_start

                if elapsed_zoom_dwell < ZOOM_DWELL_TIME:
                    # Visual dwell indicator (purple arc)
                    progress = min(elapsed_zoom_dwell / ZOOM_DWELL_TIME, 1.0)
                    end_angle = int(360 * progress)

                    cv2.ellipse(
                        frame,
                        (x_cam, y_cam),
                        (35, 35),
                        -90,
                        0,
                        end_angle,
                        (255, 0, 255),
                        3
                    )
                    continue

                # ---- ZOOM ACTIVE AFTER DWELL ----
                zoom_delta = y_cam - prev_zoom_y

                # ---- DIRECT RESPONSIVE ZOOM WITH THROTTLING ----
                if abs(zoom_delta) > ZOOM_DEAD_ZONE:
                    now = time.time()
                    if now - last_zoom_step_time > ZOOM_STEP_INTERVAL:
                        if zoom_delta < 0:
                            pyautogui.hotkey('command', '+')   # zoom in
                        else:
                            pyautogui.hotkey('command', '-')   # zoom out
                        last_zoom_step_time = now

                prev_zoom_y = y_cam

                radius = int(min(60, 30 + abs(zoom_delta)))
                cv2.circle(frame, (x_cam, y_cam), radius, (255, 0, 255), 3)
                continue

            elif current_mode == MODE_SCROLL:
                if prev_scroll_y is None:
                    prev_scroll_y = y_cam
                else:
                    scroll_delta = y_cam - prev_scroll_y
                    if abs(scroll_delta) > SCROLL_DEAD_ZONE:
                        desired_velocity = scroll_delta * 0.5
                        scroll_velocity = (
                            (1 - SCROLL_SMOOTHING) * scroll_velocity +
                            SCROLL_SMOOTHING * desired_velocity
                        )
                    else:
                        scroll_velocity *= SCROLL_INERTIA_DECAY

                    scroll_velocity = max(-MAX_SCROLL_STEP, min(scroll_velocity, MAX_SCROLL_STEP))

                    if abs(scroll_velocity) > SCROLL_MIN_VELOCITY:
                        pyautogui.scroll(-int(scroll_velocity))
                    else:
                        scroll_velocity = 0.0

                    prev_scroll_y = y_cam

                bar_x = int(prev_x + 40)
                bar_y1 = int(prev_y - SCROLL_INDICATOR_HEIGHT // 2)
                bar_y2 = int(prev_y + SCROLL_INDICATOR_HEIGHT // 2)

                cv2.line(frame, (bar_x, bar_y1), (bar_x, bar_y2), (255, 0, 0), 4)
                cv2.circle(frame, (bar_x, int(prev_y)), 6, (255, 0, 0), -1)
                continue

            # ---- CURSOR MODE ----
            dx_move = screen_x - prev_x
            dy_move = screen_y - prev_y
            movement = (dx_move**2 + dy_move**2) ** 0.5

            if movement < DEAD_ZONE:
                screen_x, screen_y = prev_x, prev_y

            speed = min((movement + 1) * ACCELERATION_SCALE, 3.0)

            curr_x = prev_x + (screen_x - prev_x) * speed / smoothening
            curr_y = prev_y + (screen_y - prev_y) * speed / smoothening

            curr_x = max(0, min(curr_x, screen_width - 1))
            curr_y = max(0, min(curr_y, screen_height - 1))

            pyautogui.moveTo(curr_x, curr_y)

            # ----- DWELL CLICK LOGIC -----
            current_time = time.time()

            if dwell_start_time is None:
                dwell_start_time = current_time
            else:
                if last_dwell_x is None:
                    last_dwell_x, last_dwell_y = curr_x, curr_y

                dx_dwell = curr_x - last_dwell_x
                dy_dwell = curr_y - last_dwell_y
                dwell_movement = (dx_dwell**2 + dy_dwell**2) ** 0.5

                if dwell_movement < DWELL_RADIUS:
                    elapsed = current_time - dwell_start_time
                    progress = min(elapsed / DWELL_TIME, 1.0)

                    center = (int(curr_x), int(curr_y))
                    end_angle = int(360 * progress)

                    cv2.ellipse(
                        frame,
                        center,
                        (DWELL_INDICATOR_RADIUS, DWELL_INDICATOR_RADIUS),
                        -90,
                        0,
                        end_angle,
                        (0, 255, 0),
                        3
                    )

                    if elapsed >= DWELL_TIME:
                        pyautogui.click()
                        dwell_start_time = None
                        click_cooldown = CLICK_COOLDOWN_FRAMES
                else:
                    dwell_start_time = current_time

                last_dwell_x, last_dwell_y = curr_x, curr_y

            prev_x, prev_y = curr_x, curr_y

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
    else:
        clicking = False
        dwell_start_time = None
        last_dwell_x, last_dwell_y = None, None
        scroll_mode = False
        prev_scroll_y = None
        scroll_velocity = 0.0
        zoom_mode = False
        prev_zoom_y = None
        zoom_velocity = 0.0
        zoom_dwell_start = None
        last_zoom_step_time = 0
        current_mode = MODE_CURSOR
    cv2.imshow("Hand Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()