import cv2
import mediapipe as mp
import time
import math
import winsound
import warnings

# Hide the Google Protobuf warning from your terminal console
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

LEFT_EYE_TOP = 386
LEFT_EYE_BOTTOM = 374
RIGHT_EYE_TOP = 159
RIGHT_EYE_BOTTOM = 145

closed_start_time = None
is_drowsy = False

# Safe fallback default values (in case window fails to load initially)
closed_threshold = 5.5
drowsy_time_limit = 1.5

def nothing(x):
    pass

# Initialize the window and sliders
window_name = 'Real-Time Drowsiness Detector'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.createTrackbar('Sensitivity (Threshold)', window_name, 55, 150, nothing)
cv2.createTrackbar('Time Buffer (Seconds)', window_name, 15, 50, nothing)

# Open the Camera
cap = cv2.VideoCapture(0)

def get_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

print("Starting Drowsiness Detector with Audio... Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            
            left_top = landmarks[LEFT_EYE_TOP]
            left_bottom = landmarks[LEFT_EYE_BOTTOM]
            right_top = landmarks[RIGHT_EYE_TOP]
            right_bottom = landmarks[RIGHT_EYE_BOTTOM]

            left_dist = get_distance(left_top, left_bottom) * width
            right_dist = get_distance(right_top, right_bottom) * width
            avg_dist = (left_dist + right_dist) / 2.0

            if avg_dist < closed_threshold:
                if closed_start_time is None:
                    closed_start_time = time.time()
                else:
                    elapsed_time = time.time() - closed_start_time
                    if elapsed_time >= drowsy_time_limit:
                        is_drowsy = True
            else:
                closed_start_time = None
                is_drowsy = False

            if is_drowsy:
                cv2.rectangle(frame, (0, 0), (width, 60), (0, 0, 255), -1)
                cv2.putText(frame, "!!! WAKE UP !!! DROWSINESS DETECTED", (30, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3)
                winsound.Beep(1000, 200)
            else:
                cv2.rectangle(frame, (0, 0), (width, 40), (0, 255, 0), -1)
                cv2.putText(frame, f"Eye Dist: {avg_dist:.1f} | Target: {closed_threshold:.1f} | Buffer: {drowsy_time_limit:.1f}s", 
                            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    # CRITICAL FIX: Show the window FIRST so Windows renders it into existence
    cv2.imshow(window_name, frame)

    # NOW read the slider data safely for the NEXT upcoming frame
    try:
        closed_threshold = cv2.getTrackbarPos('Sensitivity (Threshold)', window_name) / 10.0
        drowsy_time_limit = cv2.getTrackbarPos('Time Buffer (Seconds)', window_name) / 10.0
    except cv2.error:
        pass # Silently continue with old values if a transient glitch occurs

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
face_mesh.close()
