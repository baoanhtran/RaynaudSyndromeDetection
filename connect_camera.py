import cv2
import numpy as np
import time
import json
# from capture_hand import get_coordinates

TEMPERATURE_MIN = 20 # Température minimale de la caméra en °C
TEMPERATURE_MAX = 36 # Température maximale de la caméra en °C

list_of_points = [] # Liste pour stocker les points où l'utilisateur a cliqué
temperatures_dict = {} # Dictionnaire pour stocker les températures à différents points
fixed_start_time = None # Le temps de démarrage de l'application
start_time = None # Le temps de démarrage de la mise à jour des températures

def initialize_camera():
    thermal_camera = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Ouvrir la caméra thermique
    thermal_camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y','1','6',' ')) # Définir le codec pour la caméra thermique, Y16 est un format de pixel 16 bits
    thermal_camera.set(cv2.CAP_PROP_CONVERT_RGB, 0) # Désactiver la conversion en RGB
    return thermal_camera

def read_thermal_frame(thermal_camera):
    grabbed, frame_thermal = thermal_camera.read() # Lire une image de la caméra thermique, grabbed est un booléen indiquant si l'image a été lue avec succès
    return grabbed, frame_thermal

def get_temperature(frame_thermal):
    list_of_temp = [] # Liste pour stocker les températures
    for point in list_of_points: # Boucle à travers la liste des points où l'utilisateur a cliqué
        x_mouse, y_mouse = point
        value_pointer = frame_thermal[y_mouse, x_mouse][0] # Obtenir la valeur du pixel à la position du clic de la souris (indice 0 car l'image est en niveaux de gris)
        temperature_pointer = (value_pointer / 255.) * (TEMPERATURE_MAX - TEMPERATURE_MIN) + TEMPERATURE_MIN # Normaliser la température à la plage de la caméra
        list_of_temp.append(temperature_pointer) # Ajouter la température à la liste des températures
    return list_of_temp

def display_frame(frame_thermal, list_of_temp):
    cv2.normalize(frame_thermal, frame_thermal, 0, 255, cv2.NORM_MINMAX) # Normaliser l'image pour affichage en niveaux de gris
    frame_thermal = np.uint8(frame_thermal) # Convertir l'image en entier non signé 8 bits
    frame_thermal = cv2.applyColorMap(frame_thermal, cv2.COLORMAP_INFERNO) # Appliquer la carte de couleurs Inferno au cadre
    for point in list_of_points: # Boucle à travers la liste des points où l'utilisateur a cliqué
        x_mouse, y_mouse = point
        cv2.circle(frame_thermal, (x_mouse, y_mouse), 2, (255, 255, 255), -1) # Dessiner un cercle blanc à la position du clic de la souris
        temp = list_of_temp[list_of_points.index(point)] # Obtenir la température correspondante à ce point
        cv2.putText(frame_thermal, "{0:.1f}".format(temp), (x_mouse, y_mouse), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA) # Afficher la température à côté du point
    cv2.imshow("Measuring window", frame_thermal) # Afficher le cadre

def get_coordinates():
    with open("coordinates.txt", "r") as f:
        lines = f.readlines()
        coordinates = []
        for line in lines:
            x, y, temp = line.strip().split()
            coordinates.append((int(x), int(y)))

    return coordinates

def start_measure():
    global start_time, list_of_points
    list_of_points = get_coordinates()
    thermal_camera = initialize_camera() # Initialiser la caméra thermique
    grabbed, frame_thermal = read_thermal_frame(thermal_camera) # Lire une image de la caméra
    cv2.imshow("Measuring window", frame_thermal) # Afficher l'image
    start_time = time.time() # Obtenir le temps actuel
    while True:
        grabbed, frame_thermal = read_thermal_frame(thermal_camera) # Lire une image de la caméra
        if not grabbed: # Si l'image n'a pas été lue avec succès, sortir de la boucle
            break
        list_of_temp = get_temperature(frame_thermal) # Obtenir les températures à différents points
        display_frame(frame_thermal, list_of_temp) # Afficher l'image avec les températures
        time_saved = time.time() - start_time
        temperatures_dict[round(time_saved, 2)] = list_of_temp
        key = cv2.waitKey(1) # Attendre une touche pressée
        if key == 27:  # Si la touche Echap est pressée, quitter la boucle
            break

    cv2.destroyAllWindows() # Fermer toutes les fenêtres

    with open('temperatures.json', 'w') as f: # Enregistrer les températures dans un fichier JSON
        json.dump(temperatures_dict, f, indent=4)