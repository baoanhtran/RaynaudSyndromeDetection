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

def ajouter_points(temps, temperatures_moyennes):
    x = temps
    y = temperatures_moyennes

    all_x_added = []
    all_y_added = []

    i = 0
    while i < len(y) - 1:
        delta_T = abs(y[i + 1] - y[i])
        if delta_T >= 0.4:
            no_points = int(round(delta_T / 0.25) + 1)
            x_ajt = np.linspace(x[i], x[i + 1], no_points)
            y_ajt = np.linspace(y[i], y[i + 1], no_points)
            x_ajt = x_ajt[1:-1]
            y_ajt = y_ajt[1:-1]

            all_x_added.extend(x_ajt)
            all_y_added.extend(y_ajt)

            x = np.concatenate((x[:i + 1], x_ajt, x[i + 1:]))
            y = np.concatenate((y[:i + 1], y_ajt, y[i + 1:]))
            i += no_points - 2
        i += 1
    return np.array(x), np.array(y), (all_x_added, all_y_added)

def T_moyenne(temperatures):
    return np.mean([temperatures[doigt] for doigt in range(1, 8)], axis=0)
    
def Tlag(temps_2, temperatures_2, ordre):
    coef_2 = np.polyfit(temps_2, temperatures_2, ordre)
    poly_2 = np.poly1d(coef_2)
    indice = snl.find_peaks(poly_2(temps_2))[0]
    lag = temps_2[(indice[0])]

    return lag, indice[0]

def Gmax(temps_1, temperatures_1, ordre):
    coef_1 = np.polyfit(temps_1, temperatures_1, ordre)
    poly_d1 = np.poly1d(coef_1)
    indice_max = snl.find_peaks(poly_d1(temps_1))[0]  
    list_max = []
    for i in indice_max:
        list_max.append(poly_d1(temps_1)[i])

    i_max= list(poly_d1(temps_1)).index(max(list_max))
    
    return max(list_max), i_max

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

def tracer_donnees_global(temps, temperatures_moyennes, n, step, fichier_txt, nom):
    # Générer la fonction approximative
    poly_approx = retrouve_polynome_fit(temps, temperatures_moyennes, n)

    # Retrouve la derivée d'ordre 1 et 2
    temps_derivee, temperatures_moyennes_derivee = derivee_list(temps, temperatures_moyennes, step)
    temps_derivee_2, temperatures_moyennes_derivee_2 = derivee_list(temps_derivee, temperatures_moyennes_derivee, step)

    # Générer la fonction approximative derivée d'ordre 1 et 2
    poly_1 = retrouve_polynome_fit(temps_derivee, temperatures_moyennes_derivee, n-1)
    poly_2 = retrouve_polynome_fit(temps_derivee_2, temperatures_moyennes_derivee_2, n-2)

    # Création de la figure et des sous-graphiques
    fig, axs = plt.subplots(3, 2, figsize=(14, 14)) # 3 sous-graphiques, 2 colonnes

    T_lag, i_lag = Tlag(temps_derivee_2, temperatures_moyennes_derivee_2, n-2)
    G_max, i_max = Gmax(temps_derivee, temperatures_moyennes_derivee, n-1)
    T_lag = round(T_lag, 2)
    G_max = round(G_max, 2)

    # Tracer le polynôme
    temps, temperatures_moyennes, point_ajoute = ajouter_points(temps, temperatures_moyennes)
 
    # Tracé de la première figure (Polynôme)
    axs[0, 0].plot(temps, poly_approx(temps), 'r', label=f"Polynôme approximatif d'ordre {n}")
    axs[0, 0].scatter(temps, temperatures_moyennes, label='Température moyenne', marker='.')
    axs[0, 0].set_title('Données originales (Courbe de réchauffement) et polynôme approximatif')
    axs[0, 0].set_ylim((20, 36))
    axs[0, 0].set_ylabel('Température:°C')
    axs[0, 0].grid(True)
    axs[0, 0].legend()

    # Tracé de la deuxième figure (Première dérivée)
    axs[1, 0].scatter(temps_derivee, temperatures_moyennes_derivee, s=10)
    axs[1, 0].plot(temps_derivee, poly_1(temps_derivee), 'y', label="Polynôme approximative du derviée l'ordre 1 ")
    axs[1, 0].plot(temps_derivee[i_max], (poly_1(temps_derivee))[i_max], 'r*', label=f"Gmax = {G_max}°C/min")
    axs[1, 0].set_title('Première dérivée')
    axs[1, 0].set_ylabel('°C/min')
    axs[1, 0].grid(True)
    axs[1, 0].legend()


    # Tracé de la troisième figure (Deuxième dérivée)
    axs[2, 0].scatter(temps_derivee_2, temperatures_moyennes_derivee_2, s=10)
    axs[2, 0].plot(temps_derivee_2, poly_2(temps_derivee_2), 'g-', label="Polynôme approximative du derviée l'ordre 2")
    axs[2, 0].plot(temps_derivee_2[i_lag], (poly_2(temps_derivee_2))[i_lag], 'r*', label=f'Tlag : {T_lag} min')
    axs[2, 0].set_title('Deuxième dérivée')
    axs[2, 0].set_xlabel('Temps: min')
    axs[2, 0].set_ylabel('°C/min²')
    axs[2, 0].grid(True)
    axs[2, 0].legend()

    log_G_max = round(np.log10(G_max), 1)
    log_T_lag = round(np.log10(T_lag), 1)
    R = round((temperatures_moyennes[-1] / T_pre(fichier_txt)) * 100, 1)
    test_resultat, bool_factors = diagnostic(log_G_max, log_T_lag, R)

    # Ajouter le tableau dans la deuxième colonne
    donnees_tableau = [[
                ["Facteur", f"Patient ({nom})" , "Non Raynaud", "Avec Raynaud"],
                ["Log_10(Gmax)", f"{log_G_max}", ">0.15", "<=0.15"],
                ["Log_10(Tlag)", f"{log_T_lag}", "<0.5", ">=0.5"],
                ["R%", f"{R}%", ">75%", "<=75%"]
            ],
            [
                ["Facteur", "Résultat"],
                ["Log_10(Gmax)", bool_factors[0]],
                ["Log_10(Tlag)", bool_factors[1]],
                ["R%", bool_factors[2]]
            ],
            [
                ["Résultat", test_resultat],
            ]
        ]
    
    # Titre du tableau
    titre_tableau = ["Traitement des données", "Résultat de l'analyse", "Diagnostic"]

    for i in range(3):
        tableau = axs[i, 1].table(cellText=donnees_tableau[i], bbox=[0, 0, 1, 1], cellLoc='center', fontsize=20)
        axs[i, 1].axis('off') # Supprimer les axes du deuxième sous-graphique
        axs[i, 1].annotate(titre_tableau[i], xy=(0.5, 1.05), xycoords='axes fraction', ha='center', fontsize=20)

        if i == 2:
            tableau.auto_set_font_size(False)
            tableau.set_fontsize(16)
    
    # Ajuster l'espacement entre les sous-graphiques
    plt.tight_layout(pad=3.5)

    # Sauvegarder la figure
    plt.savefig(f"Résultats/{nom}.png")
    
    # Afficher la figure
    plt.show()

def diagnostic(log_G_max, log_T_lag, R):
    bool_factors = ["Non Raynaud", "Non Raynaud", "Non Raynaud"]

    if log_G_max <= 0.15:
        bool_factors[0] = "Avec Raynaud"
    if log_T_lag >= 0.5:
        bool_factors[1] = "Avec Raynaud"
    if R <= 75:
        bool_factors[2] = "Avec Raynaud"

    if bool_factors.count("Avec Raynaud") >= 2:
        return "Positif", bool_factors
    else:
        return "Négatif", bool_factors
    
def tracer(nom):
    n = 9
    step = 1

    fichier_txt = f"{nom}/coordinates.txt"
    nom_fichier = f"{nom}/temperatures.json"

    #Traiter les données
    donnees = lire_fichier_json(nom_fichier)
    temps, temperatures = traiter_donnees(donnees)
    temperatures_moyennes= T_moyenne(temperatures)
    
    #Trier les données, prend juste chaque 15 seconde
    temps_n = []
    temperature_n = []

    # for i in range(0, len(temperatures_moyennes), 50):
    for i in range(0, len(temperatures_moyennes)):
        temps_n.append(temps[i])
        temperature_n.append(temperatures_moyennes[i])
    
    temperatures_moyennes = np.array(temperature_n)
    temps = np.array(temps_n)
    
    tracer_donnees_global(temps, temperatures_moyennes, n, step, fichier_txt, nom)