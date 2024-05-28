import cv2

def check_coordinates():
    # Read the image with the drawn points.
    img = cv2.imread("coordinates.jpg")

    # Display the image with the drawn points in a window named "Coordinates".
    cv2.imshow("Coordinates", img)

    # Wait for the user to press any key to close the window.
    cv2.waitKey(0)

    # Close all windows when done.
    cv2.destroyAllWindows()