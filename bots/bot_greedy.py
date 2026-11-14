
# bot_greedy.py

def calculer_distance(position_1, position_2):

    x1, y1 = position_1
    x2, y2 = position_2

    return abs(x1 - x2) + abs(y1 - y2)


def choisir_direction(position_actuelle, position_cible):

    x, y = position_actuelle
    cible_x, cible_y = position_cible

    if cible_x > x:
        return "RIGHT"

    if cible_x < x:
        return "LEFT"

    if cible_y > y:
        return "DOWN"

    if cible_y < y:
        return "UP"

    return "WAIT"


def decide(observation):

    position = observation["ma_position"]
    base = observation["ma_base"]

    sac = observation["mon_sac"]

    energie = observation["mon_energie"]

    ressources = observation["ressources"]

    # ------------------------------------------------
    # DECIDER S'IL FAUT RENTRER A LA BASE
    # ------------------------------------------------

    if len(sac) >= observation["capacite_sac"]:

        if position == base:
            return "DEPOSIT"

        return choisir_direction(position, base)

    if energie < 15:

        if position == base:
            return "WAIT"

        return choisir_direction(position, base)

    # ------------------------------------------------
    # CHERCHER LA MEILLEURE RESSOURCE
    # ------------------------------------------------

    if len(ressources) == 0:
        return "WAIT"

    meilleure_ressource = None
    meilleure_note = -1

    for ressource in ressources:

        position_ressource = (
            ressource["x"],
            ressource["y"]
        )

        distance = calculer_distance(
            position,
            position_ressource
        )

        valeur = ressource["valeur"]

        note = valeur / (distance + 1)

        if note > meilleure_note:

            meilleure_note = note
            meilleure_ressource = ressource

    # ------------------------------------------------
    # ALLER VERS LA RESSOURCE
    # ------------------------------------------------

    cible = (
        meilleure_ressource["x"],
        meilleure_ressource["y"]
    )

    if position == cible:

        return "COLLECT"

    return choisir_direction(position, cible)
