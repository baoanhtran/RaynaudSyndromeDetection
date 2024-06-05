from connect_camera import start_measure
from get_fingers_coordinates import get_coordinates
from check_coordinates import check_coordinates
from traitement_donnee import tracer
import tkinter as tk
from tkinter import messagebox

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Raynaud Syndrome Detector")
        self.geometry("400x400")

        # Étiquette pour le nom du patient
        self.name_label = tk.Label(self, text="Nom du patient")
        self.name_label.pack(pady=20)

        # Champ de saisie pour le nom du patient
        self.name_entry = tk.Entry(self)
        self.name_entry.pack(pady=20)

        # Bouton pour obtenir les coordonnées et les températures initiales
        self.get_coordinates_btn = tk.Button(self, text="Obtenir les coordonnées et les températures initiales", command=self.get_coordinates)
        self.get_coordinates_btn.pack(pady=20)

        # Bouton pour vérifier les coordonnées
        self.check_coordinates_btn = tk.Button(self, text="Vérifier les coordonnées", command=self.check_coordinates)
        self.check_coordinates_btn.pack(pady=20)

        # Bouton pour commencer à mesurer
        self.measure_btn = tk.Button(self, text="Commencer à mesurer", command=self.start_measuring)
        self.measure_btn.pack(pady=20)

        # Bouton pour afficher le résultat
        self.show_graph_btn = tk.Button(self, text="Afficher le résultat", command=self.show_graph)
        self.show_graph_btn.pack(pady=20)

        # Bouton pour quitter
        self.quit_btn = tk.Button(self, text="Quitter", command=self.quit)
        self.quit_btn.pack(pady=20)

    # Méthode pour démarrer la mesure des températures
    def start_measuring(self):
        nom = self.name_entry.get().strip()
        if nom == "":
            messagebox.showerror("Erreur", "Veuillez entrer le nom du patient")
            return
        start_measure(nom)
        messagebox.showinfo("Succès", "Températures sauvegardées")

    # Méthode pour vérifier les coordonnées des doigts
    def check_coordinates(self):
        nom = self.name_entry.get().strip()
        if nom == "":
            messagebox.showerror("Erreur", "Veuillez entrer le nom du patient")
            return
        check_coordinates(nom)

    # Méthode pour obtenir les coordonnées et les températures initiales
    def get_coordinates(self):
        nom = self.name_entry.get().strip()
        if nom == "":
            messagebox.showerror("Erreur", "Veuillez entrer le nom du patient")
            return
        get_coordinates(nom)
        messagebox.showinfo("Succès", "Coordonnées et températures sauvegardées")

    # Méthode pour afficher le graphique des résultats
    def show_graph(self):
        nom = self.name_entry.get().strip()
        if nom == "":
            messagebox.showerror("Erreur", "Veuillez entrer le nom du patient")
            return
        tracer(nom)

    # Méthode pour quitter l'application
    def quit(self):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()