
# bot_secret.py

def distance(position_1, position_2):

    x1, y1 = position_1
    x2, y2 = position_2

    return abs(x1 - x2) + abs(y1 - y2)


def choisir_direction(position, cible):

    x, y = position
    cible_x, cible_y = cible

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

    energie = observation["mon_energie"]
    sac = observation["mon_sac"]

    ressources = observation["ressources"]

    capacite = observation["capacite_sac"]

    # ----------------------------------------------
    # VALEUR DES RESSOURCES DEJA COLLECTEES
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
    # EVALUER LE RETOUR A LA BASE
    # ----------------------------------------------

    distance_retour = distance(position, base)

    energie_pour_rentrer = distance_retour + 5

    sac_plein = len(sac) >= capacite

    energie_faible = energie <= energie_pour_rentrer + 8

    # Si le sac contient des ressources,
    # on privilégie le retour à la base.

    if sac_plein or (energie_faible and len(sac) > 0):

        if position == base:
            return "DEPOSIT"

        return choisir_direction(position, base)

    # Si le robot est à court d'énergie,
    # il doit recharger à sa base.

    if energie <= energie_pour_rentrer:

        if position == base:
            return "WAIT"

        return choisir_direction(position, base)

    # ----------------------------------------------
    # CHERCHER LA MEILLEURE OPPORTUNITE
    # ----------------------------------------------

    meilleure_ressource = None
    meilleure_note = -1

    for ressource in ressources:

        cible = (ressource["x"], ressource["y"])

        distance_aller = distance(position, cible)

        distance_retour = distance(cible, base)

        cout_total = distance_aller + distance_retour

        # On vérifie que le robot peut effectuer
        # le trajet aller-retour.

        energie_necessaire = (
            cout_total + 2 + 5
        )

        if energie < energie_necessaire:
            continue

        valeur = ressource["valeur"]

        # Bonus pour les ressources rares
        # et pénalité pour les trajets longs.

        note = valeur / (cout_total + 1)

        if note > meilleure_note:

            meilleure_note = note

            meilleure_ressource = cible

    # ----------------------------------------------
    # AUCUNE CIBLE INTERESSANTE
    # ----------------------------------------------

    if meilleure_ressource is None:

        if position == base:
            return "WAIT"

        return choisir_direction(position, base)

    # ----------------------------------------------
    # ALLER VERS LA CIBLE
    # ----------------------------------------------

    if position == meilleure_ressource:

        return "COLLECT"

    return choisir_direction(position, meilleure_ressource)
