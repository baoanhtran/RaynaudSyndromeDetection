import json
from matplotlib import pyplot as plt
import numpy as np

def show_graph():
    with open('temperatures.json', 'r') as f:
        temperatures_dict = json.load(f)

    time = list(temperatures_dict.keys())
    time = [float(t) for t in time]
    x_range = np.linspace(0, max(time), 1000)

    temp_keys = ['Point 1', 'Point 2', 'Point 3', 'Point 4']
    temps = [[temp[i] for temp in temperatures_dict.values()] for i in range(4)]    
    polynomials = [np.poly1d(np.polyfit(time, temp, 3)) for temp in temps]

    plt.get_current_fig_manager().window.state('zoomed')

    for i, (temp, poly, key) in enumerate(zip(temps, polynomials, temp_keys), start=1):
        plt.subplot(2, 2, i)
        plt.plot(time, temp, label=key)
        plt.plot(x_range, poly(x_range), label='Polynomial fit')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Temperature (°C)')
        plt.legend()

    plt.tight_layout()
    plt.show()