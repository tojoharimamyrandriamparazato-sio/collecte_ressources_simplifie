
# bot_hunter.py

DIRECTIONS = {

    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)

}


def trouver_chemin(depart, arrivee, largeur, hauteur, obstacle):

    file_attente = [(depart, [])]

    positions_visitees = [depart]

    while len(file_attente) > 0:

        position_actuelle, chemin = file_attente.pop(0)

        if position_actuelle == arrivee:

            return chemin

        x, y = position_actuelle

        for nom_direction, mouvement in DIRECTIONS.items():

            dx, dy = mouvement

            nouvelle_position = (x + dx, y + dy)

            nouveau_x, nouveau_y = nouvelle_position

            # Vérifier les limites de la carte

            if nouveau_x < 0 or nouveau_x >= largeur:
                continue

            if nouveau_y < 0 or nouveau_y >= hauteur:
                continue

            # Eviter l'adversaire

            if nouvelle_position == obstacle:
                continue

            # Eviter les positions déjà visitées

            if nouvelle_position in positions_visitees:
                continue

            positions_visitees.append(nouvelle_position)

            nouveau_chemin = chemin + [nom_direction]

            file_attente.append(
                (nouvelle_position, nouveau_chemin)
            )

    return []


def decide(observation):

    position = observation["ma_position"]

    base = observation["ma_base"]

    adversaire = observation["position_adversaire"]

    energie = observation["mon_energie"]

    sac = observation["mon_sac"]

    capacite = observation["capacite_sac"]

    largeur = observation["largeur_carte"]

    hauteur = observation["hauteur_carte"]

    ressources = observation["ressources"]

    # ----------------------------------------------
    # CALCULER LA DISTANCE DE RETOUR
    # ----------------------------------------------

    chemin_retour = trouver_chemin(
        position,
        base,
        largeur,
        hauteur,
        adversaire
    )

    distance_retour = len(chemin_retour)

    # ----------------------------------------------
    # DECIDER DU RETOUR
    # ----------------------------------------------

    if len(sac) >= capacite or energie <= distance_retour + 8:

        if position == base:
            return "DEPOSIT" if len(sac) > 0 else "WAIT"

        if len(chemin_retour) > 0:
            return chemin_retour[0]

        return "WAIT"

    # ----------------------------------------------
    # CHERCHER LA MEILLEURE RESSOURCE
    # ----------------------------------------------

    meilleure_note = -1

    meilleur_chemin = []

    for ressource in ressources:

        cible = (ressource["x"], ressource["y"])

        chemin_aller = trouver_chemin(
            position,
            cible,
            largeur,
            hauteur,
            adversaire
        )

        if cible != position and len(chemin_aller) == 0:
            continue

        distance_aller = len(chemin_aller)

        chemin_vers_base = trouver_chemin(
            cible,
            base,
            largeur,
            hauteur,
            adversaire
        )

        if cible != base and len(chemin_vers_base) == 0:
            continue

        distance_base = len(chemin_vers_base)

        cout_total = distance_aller + distance_base + 2

        if cout_total > energie:
            continue

        note = ressource["valeur"] / (cout_total + 1)

        if note > meilleure_note:

            meilleure_note = note

            meilleur_chemin = chemin_aller

    # ----------------------------------------------
    # AUCUNE RESSOURCE RENTABLE
    # ----------------------------------------------

    if meilleure_note == -1:

        if position == base:
            return "WAIT"

        if len(chemin_retour) > 0:
            return chemin_retour[0]

        return "WAIT"

    # ----------------------------------------------
    # EXECUTER LE PREMIER DEPLACEMENT DU CHEMIN
    # ----------------------------------------------

    if len(meilleur_chemin) == 0:

        return "COLLECT"

    return meilleur_chemin[0]
