from connect_camera import start_measure
from get_fingers_coordinates import get_coordinates
from check_coordinates import check_coordinates
# from tracer import show_graph
from traitement_donnee import main
import tkinter as tk
from tkinter import messagebox

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Raynaud Syndrome Detector")
        self.geometry("400x400")

        # Get coordinates button
        self.get_coordinates_btn = tk.Button(self, text="Get coordinates and initial temperatures", command=self.get_coordinates)
        self.get_coordinates_btn.pack(pady=20)

        # Check coordinates button
        self.check_coordinates_btn = tk.Button(self, text="Check coordinates", command=self.check_coordinates)
        self.check_coordinates_btn.pack(pady=20)

        # Start measuring button
        self.measure_btn = tk.Button(self, text="Start measuring", command=self.start_measuring)
        self.measure_btn.pack(pady=20)

        # Show graph button
        self.show_graph_btn = tk.Button(self, text="Show graph", command=self.show_graph)
        self.show_graph_btn.pack(pady=20)

        # Quit button
        self.quit_btn = tk.Button(self, text="Quit", command=self.quit)
        self.quit_btn.pack(pady=20)

    def start_measuring(self):
        start_measure()
        messagebox.showinfo("Success", "Temperature measurements saved")

    def check_coordinates(self):
        check_coordinates()

    def get_coordinates(self):
        get_coordinates()
        messagebox.showinfo("Success", "Coordinates and temperatures saved")

    def show_graph(self):
        main()

    def quit(self):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()