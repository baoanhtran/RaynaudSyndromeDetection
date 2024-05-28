import cv2
import mediapipe as mp
import numpy as np

def get_coordinates():
    chosen_index = [6, 10, 14, 18]
    chosen_coordinates = []
    # Initialize video capture with the video file.
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y','1','6',' ')) # Définir le codec pour la caméra thermique, Y16 est un format de pixel 16 bits
    cap.set(cv2.CAP_PROP_CONVERT_RGB, 0) # Désactiver la conversion en RGB

    # Setup MediaPipe Hands for hand tracking.
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.1, min_tracking_confidence=0.1)

    # Start a loop to process each frame of the video.
    while True:
        # Read a frame from the video capture object.
        success, img = cap.read()
        if not success:
            break

        # Convert grayscale image to RGB image.
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgRGB = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)

        # Process the RGB image to find hand landmarks.
        results = hands.process(imgRGB)

        # Get hand landmarks if any are detected.
        multiLandMarks = results.multi_hand_landmarks

        print(multiLandMarks) 

        # If hand landmarks are detected, iterate through them then quit the loop.
        if multiLandMarks is not None and len(multiLandMarks) == 2:
            # Iterate through each set of hand landmarks.
            for i, handLms in enumerate(multiLandMarks):
                # Draw the hand landmarks and connections on the original frame.

                # Iterate through each landmark to get its index and coordinates.
                for idx, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape  # Get the dimensions of the image.
                    cx, cy = int(lm.x * w), int(lm.y * h)  # Calculate pixel coordinates.
                    if idx in chosen_index:
                        chosen_coordinates.append([cx,cy])
                        list_of_temp = get_temperature(img, chosen_coordinates)

                # Save the temperatures corresponding to the selected points.
                with open("coordinates.txt", "w") as f:
                    for i in range(len(chosen_coordinates)):
                        f.write(f"{chosen_coordinates[i][0]} {chosen_coordinates[i][1]} {list_of_temp[i]}\n")
            
            break


    # Draw the points on the image.
    for x, y in chosen_coordinates:
        cv2.circle(img, (x, y), 2, (255, 0, 0), -1)

    # Save the image with the points drawn on it.
    cv2.imwrite("coordinates.jpg", img)
    
    # Release the video capture object and close all windows when done.
    cap.release()
    cv2.destroyAllWindows()

def get_temperature(frame_thermal, coordonnee_choisi):
    TEMPERATURE_MIN = 20 # Température minimale de la caméra en °C
    TEMPERATURE_MAX = 36 # Température maximale de la caméra en °C
    list_of_temp = [] # Liste pour stocker les températures
    for coord in coordonnee_choisi: # Boucle à travers la liste des points où l'utilisateur a cliqué
        x_mouse, y_mouse = coord
        value_pointer = frame_thermal[y_mouse, x_mouse][0] # Obtenir la valeur du pixel à la position du clic de la souris (indice 0 car l'image est en niveaux de gris)
        temperature_pointer = (value_pointer / 255.) * (TEMPERATURE_MAX - TEMPERATURE_MIN) + TEMPERATURE_MIN # Normaliser la température à la plage de la caméra
        list_of_temp.append(temperature_pointer) # Ajouter la température à la liste des températures

    return list_of_temp