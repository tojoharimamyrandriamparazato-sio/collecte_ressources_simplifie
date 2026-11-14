
# bot_smart.py

def distance(position_1, position_2):

    x1, y1 = position_1
    x2, y2 = position_2

    return abs(x1 - x2) + abs(y1 - y2)


def choisir_direction(position, cible):

    x, y = position
    cible_x, cible_y = cible

    if x < cible_x:
        return "RIGHT"

    if x > cible_x:
        return "LEFT"

    if y < cible_y:
        return "DOWN"

    if y > cible_y:
        return "UP"

    return "WAIT"


def decide(observation):

    position = observation["ma_position"]
    base = observation["ma_base"]

    energie = observation["mon_energie"]

    sac = observation["mon_sac"]

    ressources = observation["ressources"]

    capacite = observation["capacite_sac"]

    # ----------------------------------------------
    # CALCULER LA VALEUR DU SAC
    # ----------------------------------------------

    valeurs = {
        "BOIS": 2,
        "PIERRE": 3,
        "FER": 5,
        "OR": 10,
        "CRISTAL": 15
    }

    valeur_sac = 0

    for ressource in sac:

        valeur_sac += valeurs[ressource]

    # ----------------------------------------------
    # DECIDER DE RENTRER A LA BASE
    # ----------------------------------------------

    distance_base = distance(position, base)

    energie_necessaire = distance_base + 5

    if len(sac) >= capacite:

        if position == base:
            return "DEPOSIT"

        return choisir_direction(position, base)

    if energie <= energie_necessaire + 5:

        if position == base:
            return "WAIT"

        return choisir_direction(position, base)

    # ----------------------------------------------
    # CHERCHER UNE RESSOURCE RENTABLE
    # ----------------------------------------------

    meilleure_cible = None
    meilleure_note = -1

    for ressource in ressources:

        cible = (
            ressource["x"],
            ressource["y"]
        )

        distance_aller = distance(position, cible)

        distance_retour = distance(cible, base)

        cout_total = distance_aller + distance_retour

        valeur = ressource["valeur"]

        if cout_total == 0:
            cout_total = 1

        rentabilite = valeur / cout_total

        if rentabilite > meilleure_note:

            meilleure_note = rentabilite

            meilleure_cible = cible

    # ----------------------------------------------
    # SE DEPLACER
    # ----------------------------------------------

    if meilleure_cible is None:

        if position == base:
            return "WAIT"

        return choisir_direction(position, base)

    if position == meilleure_cible:

        return "COLLECT"

    return choisir_direction(position, meilleure_cible)
