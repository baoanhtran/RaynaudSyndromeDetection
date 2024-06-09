import cv2
import numpy as np
import time
import json
import tkinter as tk
from threading import Thread

TEMPERATURE_MIN = 20  # Température minimale de la caméra en °C
TEMPERATURE_MAX = 36  # Température maximale de la caméra en °C

list_of_points = []  # Liste pour stocker les points où l'utilisateur a cliqué
temperatures_dict = {}  # Dictionnaire pour stocker les températures à différents points
start_time = None  # Le temps de démarrage de la mise à jour des températures
last_save_time = None  # Le temps de la dernière sauvegarde des températures
stop_flag = False # Drapeau pour arrêter le thread de mise à jour du timer
root = None  # Fenêtre racine pour l'interface graphique du timer
prev_frame_temp = None  # Température de la trame précédente
current_frame_temp = None  # Température de la trame actuelle

def initialize_camera():
    thermal_camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Ouvrir la caméra thermique
    thermal_camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', '1', '6', ' '))  # Définir le codec pour la caméra thermique, Y16 est un format de pixel 16 bits
    thermal_camera.set(cv2.CAP_PROP_CONVERT_RGB, 0)  # Désactiver la conversion en RGB
    return thermal_camera

def read_thermal_frame(thermal_camera):
    grabbed, frame_thermal = thermal_camera.read()  # Lire une image de la caméra thermique, grabbed est un booléen indiquant si l'image a été lue avec succès
    return grabbed, frame_thermal

def get_temperature(frame_thermal):
    list_of_temp = []  # Liste pour stocker les températures
    for point in list_of_points:  # Boucle à travers la liste des points où l'utilisateur a cliqué
        x_mouse, y_mouse = point
        value_pointer = frame_thermal[y_mouse, x_mouse][0]  # Obtenir la valeur du pixel à la position du clic de la souris (indice 0 car l'image est en niveaux de gris)
        temperature_pointer = (value_pointer / 255.) * (TEMPERATURE_MAX - TEMPERATURE_MIN) + TEMPERATURE_MIN  # Normaliser la température à la plage de la caméra
        list_of_temp.append(temperature_pointer)  # Ajouter la température à la liste des températures
    return list_of_temp

def display_frame(frame_thermal, list_of_temp):
    cv2.normalize(frame_thermal, frame_thermal, 0, 255, cv2.NORM_MINMAX)  # Normaliser l'image pour affichage en niveaux de gris
    frame_thermal = np.uint8(frame_thermal)  # Convertir l'image en entier non signé 8 bits
    frame_thermal = cv2.applyColorMap(frame_thermal, cv2.COLORMAP_INFERNO)  # Appliquer la carte de couleurs Inferno au cadre
    for point in list_of_points:  # Boucle à travers la liste des points où l'utilisateur a cliqué
        x_mouse, y_mouse = point
        cv2.circle(frame_thermal, (x_mouse, y_mouse), 2, (255, 255, 255), -1)  # Dessiner un cercle blanc à la position du clic de la souris
        temp = list_of_temp[list_of_points.index(point)]  # Obtenir la température correspondante à ce point
        cv2.putText(frame_thermal, "{0:.1f}".format(temp), (x_mouse, y_mouse), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)  # Afficher la température à côté du point
    cv2.imshow("Fenêtre de mesure", frame_thermal)  # Afficher le cadre

def get_coordinates(nom):  # Fonction pour obtenir les coordonnées initiales des doigts
    with open(f"{nom}/coordinates.txt", "r") as f:
        lines = f.readlines()
        coordinates = []
        for line in lines:
            x, y, temp = line.strip().split()  # Séparer les coordonnées et la température
            coordinates.append((int(x), int(y)))
    return coordinates

def update_timer(timer_label, diff_label):
    global prev_frame_temp, stop_flag, current_frame_temp
    while not stop_flag:
        if start_time is not None:
            elapsed_time = time.time() - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            timer_label.config(text=f"Temps écoulé: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

            if prev_frame_temp:
                if current_frame_temp:
                    mean_temp_diff = abs(current_frame_temp - prev_frame_temp)
                    diff_label.config(text=f"Variation de température: {mean_temp_diff:.2f}°C")
        time.sleep(0.1)

def start_measure(nom):
    global start_time, last_save_time, list_of_points, temperatures_dict, stop_flag, root, prev_frame_temp, current_frame_temp
    list_of_points = get_coordinates(nom)
    thermal_camera = initialize_camera()  # Initialiser la caméra thermique
    grabbed, frame_thermal = read_thermal_frame(thermal_camera)  # Lire une image de la caméra
    cv2.imshow("Fenêtre de mesure", frame_thermal)  # Afficher l'image
    start_time = time.time()  # Obtenir le temps actuel
    last_save_time = start_time  # Initialiser le temps de la dernière sauvegarde

    # Start the timer GUI in a separate thread
    timer_thread = Thread(target=run_timer_gui)
    timer_thread.daemon = True
    timer_thread.start()

    list_of_temp = get_temperature(frame_thermal)  # Obtenir les températures à différents points
    prev_frame_temp = np.mean(list_of_temp)

    while True:
        grabbed, frame_thermal = read_thermal_frame(thermal_camera)  # Lire une image de la caméra
        if not grabbed:  # Si l'image n'a pas été lue avec succès, sortir de la boucle
            break

        list_of_temp = get_temperature(frame_thermal) # Obtenir les températures à différents points
        display_frame(frame_thermal, list_of_temp)  # Afficher l'image avec les températures

        current_time = time.time()
        if current_time - last_save_time >= 15:  # Vérifier si 15 secondes se sont écoulées depuis la dernière sauvegarde
            if current_frame_temp is not None:
                prev_frame_temp = current_frame_temp

            current_frame_temp = np.mean(list_of_temp) 

            time_saved = current_time - start_time
            temperatures_dict[round(time_saved, 2)] = list_of_temp
            last_save_time = current_time  # Mettre à jour le temps de la dernière sauvegarde

        key = cv2.waitKey(1)  # Attendre une touche pressée
        if key == 27:  # Si la touche Echap est pressée, quitter la boucle
            break

    cv2.destroyAllWindows()  # Fermer toutes les fenêtres
    stop_flag = True  # Arrêter le thread de mise à jour du timer
    root.after(1, root.destroy)  # Fermer la fenêtre du timer

    with open(f'{nom}/temperatures.json', 'w') as f:  # Enregistrer les températures dans un fichier JSON
        json.dump(temperatures_dict, f, indent=4)

def run_timer_gui():
    global root
    root = tk.Tk()
    root.title("Minuteur")
    root.resizable(False, False)

    timer_label = tk.Label(root, text="Temps écoulé: 00:00:00", font=("Helvetica", 16))
    timer_label.pack(padx=20, pady=20)

    diff_label = tk.Label(root, text="Variation de température: 0.00°C", font=("Helvetica", 16))
    diff_label.pack(padx=20, pady=20)

    # Start the timer update thread
    timer_update_thread = Thread(target=update_timer, args=(timer_label, diff_label))
    timer_update_thread.daemon = True
    timer_update_thread.start()

    root.mainloop()
