import cv2
import torch

# Verify your GPU is still being recognized for the CV pipeline
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Computer Vision pipeline running on: {device}")

# Open a connection to your default webcam (0 is usually the built-in camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam. Check your privacy settings or camera connection.")
    exit()

print("Webcam active! Press 'q' on your keyboard to close the window.")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Add a visual anchor text to the screen
    cv2.putText(frame, f"Device: {device} | Press 'q' to exit", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display the resulting live footage window
    cv2.imshow('Real-Time Camera Test', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clear everything out when done
cap.release()
cv2.destroyAllWindows()
