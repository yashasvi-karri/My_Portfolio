import cv2
import mediapipe as mp
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from helpers import convert_into_numeric_pairs, new_pairs_2, convert_angle
import time


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic


def output_prediction_array(X, loaded_model):
    X = np.array(X)
    predictions = loaded_model.predict(X)
    predicted_label = np.argmax(predictions, axis=1)
    return predicted_label[0]

def make_prediction(X, loaded_model):
    X = np.array(X)
    X = X[np.newaxis, :, :]
    # print(X.shape)

    predictions = loaded_model.predict(X)
    # print("Predictions_TRIAL:", predictions)
    predicted_label = np.argmax(predictions, axis=1)
    # print("Predictions:", predicted_label)
    counts = np.bincount(predicted_label)
    predicted_label = np.argmax(counts)
    class_names = {
        0: "Jumping Jack",
        1: "Pull-up",
        2: "Push-up",
        3: "Sit-up",
        4: "Squat"
    }
    text = class_names.get(predicted_label)
    return text

def display_prediction(frame, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 3.0
    color = (0, 0, 255)  # BGR color tuple
    thickness = 10
    cv2.putText(frame, text, (100, 100), font, font_scale, color, thickness)
    
def run_on_video(data):
    BG_COLOR = (192, 192, 192)  # gray
    frame_index = 0  # Counter to keep track of frame index
    buffer_size = 50  # Number of frames in the sequence buffer
    frame_buffer = []

    with mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=True,
            refine_face_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
    ) as holistic:
        user_input = input("Do you want to start tracking your activity? (yes/no): ")
        if user_input.lower() == "yes":
            while True:
                print("Get ready... Starting in 5 seconds.")
                time.sleep(1)
                for i in range(4, 0, -1):
                    print(f"Starting in {i}...")
                    time.sleep(1)
                print("Start moving! Tracking in progress.")

                frame_index = 0

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to capture frame from webcam.")
                        break

                    frame_index += 1

                    if frame_index % 1 == 0:  # Process every fifth frame
                        image_height, image_width, _ = frame.shape
                        results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                        if results.pose_landmarks is not None:
                            X = []
                            angles = []
                            for pair in new_pairs_2:
                                angle = convert_angle(results.pose_landmarks.landmark, pair)
                                angles.append(angle)
                            # Calculate and append the nose y-coordinate/left knee y-coordinate ratio
                            if results.pose_landmarks.landmark[0].y != 0 and results.pose_landmarks.landmark[25].y != 0:
                                ratio = results.pose_landmarks.landmark[0].y / results.pose_landmarks.landmark[25].y
                                angles.append(ratio)
                            frame_buffer.append(angles)

                            if len(frame_buffer) == buffer_size:
                                text = make_prediction(frame_buffer, loaded_model)
                                frame_buffer = []
                                display_prediction(frame, text)
                                print("EXERCISE:", text)

                                while True:
                                    user_input = input("Do you want to start another exercise? (yes/no): ")
                                    if user_input.lower() == "no":
                                        break
                                    elif user_input.lower() == "yes":
                                        break
                                    else:
                                        print("Invalid input. Please enter 'yes' or 'no'.")

                                if user_input.lower() == "no":
                                    break

                                print("Get ready for the next exercise... Starting in 5 seconds.")
                                time.sleep(1)
                                for i in range(4, 0, -1):
                                    print(f"Starting in {i}...")
                                    time.sleep(1)
                                print("Start moving! Tracking in progress.")

                        cv2.imshow("Webcam", frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                if user_input.lower() == "no":
                    break

        else:
            print("Activity tracking canceled.")


    cap.release()
    cv2.destroyAllWindows()

    return data

if __name__ == "__main__":

    # Load the trained model
    loaded_model = tf.keras.models.load_model('my_ts_model_2.keras')
    # new_pairs_2 = convert_into_numeric_pairs()
    data = {}
    cap = cv2.VideoCapture(0)
    data = run_on_video(data)
