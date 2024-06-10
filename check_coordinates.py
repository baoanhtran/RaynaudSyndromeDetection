import cv2

def check_coordinates(nom):
    # Lire l'image avec les points dessinés.
    # img = cv2.imread(f"{nom}/coordinates.jpg")
    img = cv2.imread(f"{nom}/coordinates.jpg")

    # Afficher l'image avec les points dessinés dans une fenêtre nommée "Coordinates".
    cv2.imshow("Coordinates", img)

    # Attendre que l'utilisateur appuie sur une touche pour fermer la fenêtre.
    cv2.waitKey(0)

    # Fermer toutes les fenêtres lorsqu'on a terminé.
    cv2.destroyAllWindows()