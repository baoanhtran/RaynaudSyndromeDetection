import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as snl


def lire_fichier_json(nom_fichier):
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        donnees = json.load(fichier)
    return donnees

def traiter_donnees(donnees):
    temps = []
    temperatures = {i: [] for i in range(9)}
    
    for temps_str, temp_list in donnees.items():
        temps.append(float(temps_str))
        for i, temperature in enumerate(temp_list):
            temperatures[i].append(temperature)
    
    temps = np.array(temps)
    return temps / 60, temperatures

def valeur(temps, temperatures):
    T_50 = (temperatures[-1] + temperatures[0]) / 2
    return T_50

def add_points(temps,average_temperatures):
    x = temps
    y = average_temperatures

    all_x_added = []
    all_y_added = []

    i = 0
    while i < len(y) - 1:
        delta_T = abs(y[i + 1] - y[i])
        if delta_T >= 0.4:
            no_points = int(round(delta_T / 0.25) + 1)
            x_add = np.linspace(x[i], x[i + 1], no_points)
            y_add = np.linspace(y[i], y[i + 1], no_points)
            x_add = x_add[1:-1]
            y_add = y_add[1:-1]

            all_x_added.extend(x_add)
            all_y_added.extend(y_add)

            x = np.concatenate((x[:i + 1], x_add, x[i + 1:]))
            y = np.concatenate((y[:i + 1], y_add, y[i + 1:]))
            i += no_points - 2
        i += 1
    return np.array(x), np.array(y), (all_x_added, all_y_added)

def low_pass_filter(data, alpha=1):
    """
    Applies a low pass filter to the data.
    Args : data (np.array) : The data to filter.
           alpha (float) : The filter coefficient. The closer to 1, the less filtering is applied.
    Returns : np.array : The filtered data.
    """
    filtered_data = np.zeros_like(data)
    filtered_data[0] = data[0]
    for i in range(1, len(data)):
        filtered_data[i] = alpha * data[i] + (1 - alpha) * filtered_data[i - 1]
    return filtered_data

def T_moyenne(temperatures):
    return np.mean([temperatures[doigt] for doigt in range(1, 8)], axis=0)
    
def Tlag(temps_2, temperatures_2, ordre):
    coef_2 = np.polyfit(temps_2, temperatures_2, ordre)
    poly_2 = np.poly1d(coef_2)
    indice = snl.find_peaks(poly_2(temps_2))[0]
    lag = temps_2[(indice[0])]

    return lag

def Gmax(temps_1, temperatures_1, ordre):
    coef_1 = np.polyfit(temps_1, temperatures_1, ordre)
    poly_d1 = np.poly1d(coef_1)
    indice_max = snl.find_peaks(poly_d1(temps_1))[0]  
    list_max = []
    for i in indice_max:
        list_max.append(poly_d1(temps_1)[i])
    
    return max(list_max)

def retrouve_polynome_fit(temps, températures, ordre):
    coef = np.polyfit(temps, températures, ordre)
    polynome = np.poly1d(coef)
    return polynome

def derivee_ppp(x0, x1, y0, y1):
    return (y1 - y0) / (x1 - x0)

def derivee_list(temps, temperatures_moyennes, step):
    temps_derivee = []
    temperatures_moyennes_derivee = []

    for i in range(0, len(temps)-step, step):
        temps_derivee.append((temps[i] + temps[i+step]) / 2)
        temperatures_moyennes_derivee.append(derivee_ppp(temps[i], temps[i+step], temperatures_moyennes[i], temperatures_moyennes[i+step]))

    return temps_derivee, temperatures_moyennes_derivee

def T_pre(fichier_txt):
    l3 = []
    # Lire le fichier et extraire les données
    with open(fichier_txt, 'r') as file:
        for line in file:
            parts = line.split()  # Diviser la ligne en parties
            if len(parts) >= 3:  # Vérifier qu'il y a suffisamment de colonnes
                col3 = float(parts[2])  # Troisième colonne comme flottant (décimal)
                # Ici, vous pouvez ajouter un calcul pour la dernière colonne si nécessaire
                l3.append(col3)

    return np.mean(l3)

def tracer_donnees_global(temps, temperatures_moyennes, n, step, fichier_txt):
    # Générer la fonction approximative
    poly_approx = retrouve_polynome_fit(temps, temperatures_moyennes, n)

    # Retrouve la derivée d'ordre 1 et 2
    temps_derivee, temperatures_moyennes_derivee = derivee_list(temps, temperatures_moyennes, step)
    temps_derivee_2, temperatures_moyennes_derivee_2 = derivee_list(temps_derivee, temperatures_moyennes_derivee, step)

    # Filtrer les valeurs
    temperatures_moyennes_derivee = low_pass_filter(temperatures_moyennes_derivee)
    temperatures_moyennes_derivee_2 = low_pass_filter(temperatures_moyennes_derivee_2)

    # Générer la fonction approximative derivée d'ordre 1 et 2
    poly_1 = retrouve_polynome_fit(temps_derivee, temperatures_moyennes_derivee, n-1)
    poly_2 = retrouve_polynome_fit(temps_derivee_2, temperatures_moyennes_derivee_2, n-2)

    # Création de la figure et des sous-graphiques
    fig, axs = plt.subplots(3, 2, figsize=(14, 14)) # 3 sous-graphiques, 2 colonnes

    T_lag = Tlag(temps_derivee_2, temperatures_moyennes_derivee_2, n-2)
    G_max = Gmax(temps_derivee, temperatures_moyennes_derivee, n-1)
    # Tracer le polynôme
 
    # Tracé de la première figure (Polynôme)
    axs[0, 0].plot(temps, poly_approx(temps), 'r', label=f"Polynôme approximative d'ordre {n}")
    axs[0, 0].scatter(temps, temperatures_moyennes, label='Donnée Température moyenne', marker='.')
    axs[0, 0].set_title('Tracé données originales - Réchauffement curve')
    # axs[0, 0].set_ylim((18, 36))
    axs[0, 0].set_ylabel('Température:°C')
    axs[0, 0].grid(True)
    axs[0, 0].legend()

    # Tracé de la deuxième figure (Première dérivée)
    axs[1, 0].scatter(temps_derivee, temperatures_moyennes_derivee, s=10)
    axs[1, 0].plot(temps_derivee, poly_1(temps_derivee), 'y', label=f"Gmax = {G_max}")
    # axs[1, 0].plot(temps, derivee_1(temps), 'b', label='Première dérivée')
    # axs[1, 0].plot(temps[(list(derivee_1(temps))).index(max(derivee_1(temps)))], max(derivee_1(temps)), 'r*', label=f'Gmax : {max(derivee_1(temps))}')
    axs[1, 0].set_title('Première dérivée')
    axs[1, 0].set_ylabel('°C/min')
    axs[1, 0].grid(True)
    axs[1, 0].legend()

    # Tracé de la troisième figure (Deuxième dérivée)
    # axs[2, 0].plot(temps, derivee_2(temps), 'g', label='Deuxième dérivée')
    axs[2, 0].scatter(temps_derivee_2, temperatures_moyennes_derivee_2, s=10)
    axs[2, 0].plot(temps_derivee_2, poly_2(temps_derivee_2), 'g-', label=f'Tlag : {T_lag}')
    axs[2, 0].set_title('Deuxième dérivée')
    axs[2, 0].set_xlabel('temps: min')
    axs[2, 0].set_ylabel('°C/min²')
    axs[2, 0].grid(True)
    axs[2, 0].legend()


    Tpre = round(T_pre(fichier_txt), 2)
    # Ajouter le tableau dans la deuxième colonne
    donnees_tableau = [
            [
                ["Facteur", "Patient" , "Non Raynaud", "Avec Raynaud"],
                ["Age", "âge patient", 39.2, 44.2],
                ["T_pre", f"{Tpre}°C", "30.04°C", "25.9°C"],
                ["T_debut", f"{round(temperatures_moyennes[0],2)}°C", "22.6°C", "20.02°C"],
                ["Log_10(Gmax)", f"{round(G_max,2)}",0.2351,-0.16],
                ["Log_10(Tlag)", f"{round(T_lag,2)}",0.1934,0.654],
                ["Max_R%", f"{round((temperatures_moyennes[-1]/Tpre)*100,1)}%", "131.2%", "66.6%"]
            ],
            [
                ["Facteur", "Patient_Appartient"],
                ["Age", "âge patient"],
                ["T_pre", ""],
                ["T_debut", ""],
                ["Log_10(Gmax)", "" ],
                ["Log_10(Tlag)", ""],
                ["Max_R%", ""]
            ],
            [
                ["Conclusion", ""],
                ["Test résultat", ""]
            ]
        ]
    

    for i in range(3):
        tableau = axs[i, 1].table(cellText=donnees_tableau[i], bbox=[0, 0, 1, 1], cellLoc='center', fontsize=12)
        axs[i, 1].axis('off') # Supprimer les axes du deuxième sous-graphique
        axs[i, 1].annotate(f'Titre du Tableau {i}', xy=(0.5, 1.05), xycoords='axes fraction', ha='center', fontsize=12)
    
    # Ajuster l'espacement entre les sous-graphiques
    plt.tight_layout()

    # Afficher la figure
    plt.show()

def main(): # Recevoir nom fichier, step, degre
    """
    Fonction principale pour lire les données, traiter les données et tracer les courbes.
    """
    #definir la paramètre
    n = 9
    step = 1
    list = ['ngan', 'hung', 'bao anh', 'hugo', 'ines']
    for nom in list:
        # fichier_txt = f'{nom}_final.txt'
        # nom_fichier = f'{nom}_final.json'
        fichier_txt = f"{nom}/coordinates.txt"
        nom_fichier = f"{nom}/temperatures.json"

        #Traiter les données
        donnees = lire_fichier_json(nom_fichier)
        temps, temperatures = traiter_donnees(donnees)
        temperatures_moyennes= T_moyenne(temperatures)
        
        #Trier les données, prend juste chaque 15 seconde
        temps_n = []
        temperature_n = []
        for i in range(0, len(temperatures_moyennes), 50):
            temps_n.append(temps[i])
            temperature_n.append(temperatures_moyennes[i])
        
        temperatures_moyennes = np.array(temperature_n)
        temps = np.array(temps_n)

        temps, temperatures_moyennes, point_ajoute = add_points(temps, temperatures_moyennes)
        
        tracer_donnees_global(temps, temperatures_moyennes, n, step, fichier_txt)


if __name__ == "__main__":
    main()


