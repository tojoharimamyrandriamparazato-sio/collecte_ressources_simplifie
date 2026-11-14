
import pygame
import random
import importlib


# ============================================================
# 1. CONFIGURATION GENERALE
# ============================================================

LARGEUR_CARTE = 18
HAUTEUR_CARTE = 13

TAILLE_CASE = 48

LARGEUR_PANNEAU = 300

LARGEUR_FENETRE = (
    LARGEUR_CARTE * TAILLE_CASE
    + LARGEUR_PANNEAU
)

HAUTEUR_FENETRE = HAUTEUR_CARTE * TAILLE_CASE

NOMBRE_TOURS = 1000

ENERGIE_MAX = 100
CAPACITE_SAC = 5

COUT_DEPLACEMENT = 1
COUT_COLLECTE = 2

RECHARGE_BASE = 10

DELAI_TOUR = 120


# ============================================================
# 2. COULEURS
# ============================================================

BLANC = (255, 255, 255)
NOIR = (20, 20, 20)

GRIS_FOND = (235, 235, 235)
GRIS_CASE = (215, 215, 215)
GRIS_PANNEAU = (35, 42, 55)

BLEU = (40, 120, 230)
ROUGE = (220, 65, 65)

VERT = (50, 170, 90)
JAUNE = (245, 200, 60)


# ============================================================
# 3. RESSOURCES
# ============================================================

RESSOURCES = {
    "BOIS": {
        "valeur": 2,
        "couleur": (139, 90, 43),
        "symbole": "B"
    },

    "PIERRE": {
        "valeur": 3,
        "couleur": (130, 130, 130),
        "symbole": "P"
    },

    "FER": {
        "valeur": 5,
        "couleur": (65, 125, 180),
        "symbole": "F"
    },

    "OR": {
        "valeur": 10,
        "couleur": (230, 170, 0),
        "symbole": "O"
    },

    "CRISTAL": {
        "valeur": 15,
        "couleur": (170, 80, 220),
        "symbole": "C"
    }
}


# ============================================================
# 4. CREATION DE LA CARTE
# ============================================================


def creer_carte():

    carte = {}

    positions_occupees = {
        (1, 6),
        (16, 6)
    }

    # Chaque joueur reçoit 6 ressources de chaque type.
    for nom_ressource in RESSOURCES:

        for joueur in range(2):

            for numero in range(6):

                while True:

                    if joueur == 0:
                        # Zone du joueur bleu
                        x = random.randint(2, 8)

                    else:
                        # Zone du joueur rouge
                        x = random.randint(9, 15)

                    y = random.randint(1, HAUTEUR_CARTE - 2)

                    position = (x, y)

                    if position not in positions_occupees:

                        carte[position] = nom_ressource

                        positions_occupees.add(position)

                        break

    return carte


# ============================================================
# 5. CREATION DES JOUEURS
# ============================================================

def creer_joueur(nom, position, couleur, fichier_bot):

    module_bot = importlib.import_module(fichier_bot)

    return {
        "nom": nom,
        "position": position,
        "base": position,

        "couleur": couleur,

        "energie": ENERGIE_MAX,

        "sac": [],

        "score": 0,

        "module_bot": module_bot
    }


# ============================================================
# 6. CREATION DES OBSERVATIONS
# ============================================================

def creer_observation(joueur, adversaire, carte, numero_tour):

    liste_ressources = []

    for position, nom_ressource in carte.items():

        x, y = position

        liste_ressources.append({
            "x": x,
            "y": y,
            "nom": nom_ressource,
            "valeur": RESSOURCES[nom_ressource]["valeur"]
        })

    return {
        "tour": numero_tour,

        # Informations du joueur
        "position": joueur["position"],
        "ma_position": joueur["position"],

        "base": joueur["base"],
        "ma_base": joueur["base"],

        "energie": joueur["energie"],
        "mon_energie": joueur["energie"],

        "sac": list(joueur["sac"]),
        "mon_sac": list(joueur["sac"]),

        "taille_sac": len(joueur["sac"]),
        "score": joueur["score"],

        # Adversaire
        "position_adversaire": adversaire["position"],
        "score_adversaire": adversaire["score"],

        # Ressources
        "ressources": liste_ressources,

        # Paramètres
        "capacite_sac": CAPACITE_SAC,
        "largeur_carte": LARGEUR_CARTE,
        "hauteur_carte": HAUTEUR_CARTE
    }


# ============================================================
# 7. RECUPERATION DES DECISIONS DES BOTS
# ============================================================

ACTIONS_AUTORISEES = {
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "COLLECT",
    "DEPOSIT",
    "WAIT"
}


def obtenir_action(joueur, observation):

    try:

        action = joueur["module_bot"].decide(observation)

        if not isinstance(action, str):
            return "WAIT"

        action = action.upper()

        if action not in ACTIONS_AUTORISEES:
            return "WAIT"

        return action

    except Exception as erreur:

        print(
            f"Erreur dans le bot {joueur['nom']} : {erreur}"
        )

        return "WAIT"


# ============================================================
# 8. CALCUL DES NOUVELLES POSITIONS
# ============================================================

def calculer_deplacement(position, action):

    x, y = position

    if action == "UP":
        y -= 1

    elif action == "DOWN":
        y += 1

    elif action == "LEFT":
        x -= 1

    elif action == "RIGHT":
        x += 1

    # Vérification des limites de la carte

    if not (0 <= x < LARGEUR_CARTE):
        return position

    if not (0 <= y < HAUTEUR_CARTE):
        return position

    return (x, y)


# ============================================================
# 9. EXECUTION SIMULTANEE DES DEPLACEMENTS
# ============================================================

def executer_deplacements(joueur_bleu, joueur_rouge,
                          action_bleu, action_rouge):
    """
    Les deux déplacements sont calculés avant de modifier
    les positions des joueurs.

    Si les deux joueurs veulent entrer dans la même case,
    aucun des deux ne bouge.

    Les échanges de positions sont autorisés.
    """

    actions_deplacement = {
        "UP", "DOWN", "LEFT", "RIGHT"
    }

    position_bleue_actuelle = joueur_bleu["position"]
    position_rouge_actuelle = joueur_rouge["position"]

    nouvelle_position_bleue = position_bleue_actuelle
    nouvelle_position_rouge = position_rouge_actuelle

    if (
        action_bleu in actions_deplacement
        and joueur_bleu["energie"] >= COUT_DEPLACEMENT
    ):

        nouvelle_position_bleue = calculer_deplacement(
            position_bleue_actuelle,
            action_bleu
        )

    if (
        action_rouge in actions_deplacement
        and joueur_rouge["energie"] >= COUT_DEPLACEMENT
    ):

        nouvelle_position_rouge = calculer_deplacement(
            position_rouge_actuelle,
            action_rouge
        )

    # Collision : les deux joueurs veulent la même case.

    if nouvelle_position_bleue == nouvelle_position_rouge:

        nouvelle_position_bleue = position_bleue_actuelle
        nouvelle_position_rouge = position_rouge_actuelle

    # Application des déplacements.

    if nouvelle_position_bleue != position_bleue_actuelle:

        joueur_bleu["position"] = nouvelle_position_bleue

        joueur_bleu["energie"] -= COUT_DEPLACEMENT

    if nouvelle_position_rouge != position_rouge_actuelle:

        joueur_rouge["position"] = nouvelle_position_rouge

        joueur_rouge["energie"] -= COUT_DEPLACEMENT


# ============================================================
# 10. EXECUTION DES ACTIONS COLLECTE / DEPOT / ATTENTE
# ============================================================

def executer_action_secondaire(joueur, action, carte):

    position = joueur["position"]

    # --------------------------------------------------------
    # COLLECTE
    # --------------------------------------------------------

    if action == "COLLECT":

        if joueur["energie"] < COUT_COLLECTE:
            return

        if len(joueur["sac"]) >= CAPACITE_SAC:
            return

        if position in carte:

            nom_ressource = carte[position]

            joueur["sac"].append(nom_ressource)

            del carte[position]

            joueur["energie"] -= COUT_COLLECTE

    # --------------------------------------------------------
    # DEPOT
    # --------------------------------------------------------

    elif action == "DEPOSIT":

        if position == joueur["base"]:

            for nom_ressource in joueur["sac"]:

                valeur = RESSOURCES[nom_ressource]["valeur"]

                joueur["score"] += valeur

            joueur["sac"].clear()

    # --------------------------------------------------------
    # ATTENTE
    # --------------------------------------------------------

    elif action == "WAIT":

        if position == joueur["base"]:

            joueur["energie"] = min(
                ENERGIE_MAX,
                joueur["energie"] + RECHARGE_BASE
            )


# ============================================================
# 11. EXECUTION D'UN TOUR COMPLET
# ============================================================

def executer_tour(joueur_bleu, joueur_rouge, carte, numero_tour):

    # Les deux observations sont créées avant toute action.
    # Les bots voient donc le même état initial du tour.

    observation_bleue = creer_observation(
        joueur_bleu,
        joueur_rouge,
        carte,
        numero_tour
    )

    observation_rouge = creer_observation(
        joueur_rouge,
        joueur_bleu,
        carte,
        numero_tour
    )

    # Les deux décisions sont récupérées.

    action_bleue = obtenir_action(
        joueur_bleu,
        observation_bleue
    )

    action_rouge = obtenir_action(
        joueur_rouge,
        observation_rouge
    )

    # Déplacements simultanés.

    executer_deplacements(
        joueur_bleu,
        joueur_rouge,
        action_bleue,
        action_rouge
    )

    # Collectes, dépôts et attentes.
    # Les actions sont résolues après les déplacements.

    executer_action_secondaire(
        joueur_bleu,
        action_bleue,
        carte
    )

    executer_action_secondaire(
        joueur_rouge,
        action_rouge,
        carte
    )


# ============================================================
# 12. AFFICHAGE DU TEXTE MULTILIGNE
# ============================================================

def dessiner_texte_multiligne(
    ecran,
    texte,
    x,
    y,
    police,
    couleur,
    largeur_max
):

    mots = str(texte).split(" ")

    ligne = ""

    for mot in mots:

        nouvelle_ligne = (
            mot if ligne == ""
            else ligne + " " + mot
        )

        if police.size(nouvelle_ligne)[0] <= largeur_max:

            ligne = nouvelle_ligne

        else:

            surface = police.render(
                ligne,
                True,
                couleur
            )

            ecran.blit(surface, (x, y))

            y += police.get_linesize()

            ligne = mot

    if ligne:

        surface = police.render(
            ligne,
            True,
            couleur
        )

        ecran.blit(surface, (x, y))

        y += police.get_linesize()

    return y


# ============================================================
# 13. DESSIN DE LA CARTE
# ============================================================

def dessiner_carte(
    ecran,
    carte,
    joueur_bleu,
    joueur_rouge,
    police_ressource
):

    # Fond de la carte

    ecran.fill(GRIS_FOND)

    # Grille

    for x in range(LARGEUR_CARTE):

        for y in range(HAUTEUR_CARTE):

            rectangle = pygame.Rect(
                x * TAILLE_CASE,
                y * TAILLE_CASE,
                TAILLE_CASE,
                TAILLE_CASE
            )

            pygame.draw.rect(
                ecran,
                GRIS_CASE,
                rectangle,
                1
            )

    # Ressources

    for position, nom_ressource in carte.items():

        x, y = position

        informations = RESSOURCES[nom_ressource]

        couleur = informations["couleur"]

        symbole = informations["symbole"]

        centre_x = (
            x * TAILLE_CASE
            + TAILLE_CASE // 2
        )

        centre_y = (
            y * TAILLE_CASE
            + TAILLE_CASE // 2
        )

        pygame.draw.circle(
            ecran,
            couleur,
            (centre_x, centre_y),
            17
        )

        texte = police_ressource.render(
            symbole,
            True,
            BLANC
        )

        rectangle_texte = texte.get_rect(
            center=(centre_x, centre_y)
        )

        ecran.blit(
            texte,
            rectangle_texte
        )

    # Bases

    for joueur in [joueur_bleu, joueur_rouge]:

        x, y = joueur["base"]

        centre_x = (
            x * TAILLE_CASE
            + TAILLE_CASE // 2
        )

        centre_y = (
            y * TAILLE_CASE
            + TAILLE_CASE // 2
        )

        pygame.draw.rect(
            ecran,
            joueur["couleur"],
            (
                x * TAILLE_CASE + 5,
                y * TAILLE_CASE + 5,
                TAILLE_CASE - 10,
                TAILLE_CASE - 10
            ),
            border_radius=8
        )

        texte_base = police_ressource.render(
            "B",
            True,
            BLANC
        )

        rectangle_base = texte_base.get_rect(
            center=(centre_x, centre_y)
        )

        ecran.blit(
            texte_base,
            rectangle_base
        )

    # Robots

    for joueur in [joueur_bleu, joueur_rouge]:

        x, y = joueur["position"]

        centre_x = (
            x * TAILLE_CASE
            + TAILLE_CASE // 2
        )

        centre_y = (
            y * TAILLE_CASE
            + TAILLE_CASE // 2
        )

        pygame.draw.circle(
            ecran,
            joueur["couleur"],
            (centre_x, centre_y),
            14
        )

        pygame.draw.circle(
            ecran,
            BLANC,
            (centre_x, centre_y),
            14,
            2
        )


# ============================================================
# 14. AFFICHAGE DU PANNEAU LATERAL
# ============================================================

def dessiner_panneau(
    ecran,
    joueur_bleu,
    joueur_rouge,
    numero_tour,
    police,
    police_titre,
    carte,
    partie_terminee=False
):

    debut_x = LARGEUR_CARTE * TAILLE_CASE

    pygame.draw.rect(
        ecran,
        GRIS_PANNEAU,
        (
            debut_x,
            0,
            LARGEUR_PANNEAU,
            HAUTEUR_FENETRE
        )
    )

    x = debut_x + 15

    y = 15

    largeur_texte = LARGEUR_PANNEAU - 30

    # Titre

    texte_titre = police_titre.render(
        "RESOURCE HUNTER",
        True,
        BLANC
    )

    ecran.blit(
        texte_titre,
        (x, y)
    )

    y += 45

    # Tour

    y = dessiner_texte_multiligne(
        ecran,
        f"Tour : {min(numero_tour, NOMBRE_TOURS)} / {NOMBRE_TOURS}",
        x,
        y,
        police,
        BLANC,
        largeur_texte
    )
    y += 5

    y = dessiner_texte_multiligne(
        ecran,
        f"Ressources restantes : {len(carte)}",
        x,
        y,
        police,
        BLANC,
        largeur_texte
    )

    y += 15

    # Informations des joueurs

    for joueur in [joueur_bleu, joueur_rouge]:

        pygame.draw.line(
            ecran,
            joueur["couleur"],
            (x, y),
            (x + largeur_texte, y),
            3
        )

        y += 10

        y = dessiner_texte_multiligne(
            ecran,
            joueur["nom"],
            x,
            y,
            police_titre,
            joueur["couleur"],
            largeur_texte
        )

        y = dessiner_texte_multiligne(
            ecran,
            f"Score : {joueur['score']}",
            x,
            y,
            police,
            BLANC,
            largeur_texte
        )

        y = dessiner_texte_multiligne(
            ecran,
            f"Energie : {joueur['energie']} / {ENERGIE_MAX}",
            x,
            y,
            police,
            BLANC,
            largeur_texte
        )

        y = dessiner_texte_multiligne(
            ecran,
            f"Sac : {len(joueur['sac'])} / {CAPACITE_SAC}",
            x,
            y,
            police,
            BLANC,
            largeur_texte
        )

        contenu_sac = (
            ", ".join(joueur["sac"])
            if joueur["sac"]
            else "Vide"
        )

        y = dessiner_texte_multiligne(
            ecran,
            f"Contenu : {contenu_sac}",
            x,
            y,
            police,
            BLANC,
            largeur_texte
        )

        y += 20

    # Résultat final

    if partie_terminee:

        pygame.draw.line(
            ecran,
            JAUNE,
            (x, y),
            (x + largeur_texte, y),
            3
        )

        y += 15

        texte_resultat = police_titre.render(
            "RESULTAT FINAL",
            True,
            JAUNE
        )

        ecran.blit(
            texte_resultat,
            (x, y)
        )

        y += 40
        
        if joueur_bleu["score"] > joueur_rouge["score"]:
            gagnant = joueur_bleu["nom"]
        elif joueur_rouge["score"] > joueur_bleu["score"]:
            gagnant = joueur_rouge["nom"]
        else:
            if not joueur_peut_se_deplacer(joueur_bleu) or not joueur_peut_se_deplacer(joueur_rouge):
                if joueur_rouge["energie"] > joueur_bleu["energie"]:
                    gagnant = joueur_rouge["nom"]
                elif joueur_rouge["energie"] < joueur_bleu["energie"]:
                    gagnant = joueur_bleu["nom"]
                else:
                    gagnant = "MATCH NUL"
            else:
                gagnant = "MATCH NUL"
            
        dessiner_texte_multiligne(
            ecran,
            gagnant,
            x,
            y,
            police_titre,
            JAUNE,
            largeur_texte
        )

        y += 40

        raison_fin = ""

        if not joueur_peut_se_deplacer(joueur_bleu):
            partie_terminee = True
            raison_fin = "Le joueur bleu n'a plus assez d'énergie."

        elif not joueur_peut_se_deplacer(joueur_rouge):
            partie_terminee = True
            raison_fin = "Le joueur rouge n'a plus assez d'énergie."
        elif (len(carte) == 0 and len(joueur_bleu["sac"]) == 0 and len(joueur_rouge["sac"]) == 0):
            partie_terminee = True
            raison_fin = "Toutes les ressources ont été collectées et déposées."
        
        dessiner_texte_multiligne(
            ecran,
            raison_fin,
            x,
            y,
            police_titre,
            JAUNE,
            largeur_texte
        )

def joueur_peut_se_deplacer(joueur):
    return joueur["energie"] >= COUT_DEPLACEMENT

# ============================================================
# 15. INITIALISATION DU JEU
# ============================================================

def main():

    pygame.init()

    pygame.display.set_caption(
        "Concours d'algorithmique - ESMIA Innovation - Deuxième édition"
    )

    ecran = pygame.display.set_mode(
        (LARGEUR_FENETRE, HAUTEUR_FENETRE)
    )

    horloge = pygame.time.Clock()

    police = pygame.font.SysFont(
        "DejaVu Sans",
        17
    )

    police_titre = pygame.font.SysFont(
        "DejaVu Sans",
        21,
        bold=True
    )

    police_ressource = pygame.font.SysFont(
        "DejaVu Sans",
        18,
        bold=True
    )

    # Création de la carte

    carte = creer_carte()

    # Création des joueurs

    joueur_bleu = creer_joueur(
        "JOUEUR BLEU",
        (1, 6),
        BLEU,
        "bots.bot_secret"
    )

    joueur_rouge = creer_joueur(
        "JOUEUR ROUGE",
        (16, 6),
        ROUGE,
        "bots.bot_secret"
    )

    numero_tour = 0

    partie_terminee = False

    continuer = True

    # ========================================================
    # BOUCLE PRINCIPALE
    # ========================================================

    while continuer:

        for evenement in pygame.event.get():

            if evenement.type == pygame.QUIT:

                continuer = False

        if not continuer:
            break

        if not partie_terminee:

            numero_tour += 1

            executer_tour(
                joueur_bleu,
                joueur_rouge,
                carte,
                numero_tour
            )

            if numero_tour >= NOMBRE_TOURS or (len(carte) == 0 and len(joueur_bleu["sac"]) == 0 and len(joueur_rouge["sac"]) == 0) or not joueur_peut_se_deplacer(joueur_bleu) or not joueur_peut_se_deplacer(joueur_rouge) :

                partie_terminee = True

                print("\n========== RESULTAT FINAL ==========")

                print(
                    joueur_bleu["nom"],
                    ":",
                    joueur_bleu["score"],
                    "points"
                )

                print(
                    joueur_rouge["nom"],
                    ":",
                    joueur_rouge["score"],
                    "points"
                )

                if joueur_bleu["score"] > joueur_rouge["score"]:

                    print("GAGNANT :", joueur_bleu["nom"])

                elif joueur_rouge["score"] > joueur_bleu["score"]:

                    print("GAGNANT :", joueur_rouge["nom"])

                else:

                    print("MATCH NUL")

        # Affichage de la carte

        dessiner_carte(
            ecran,
            carte,
            joueur_bleu,
            joueur_rouge,
            police_ressource
        )

        # Affichage du panneau

        dessiner_panneau(
            ecran,
            joueur_bleu,
            joueur_rouge,
            numero_tour,
            police,
            police_titre,
            carte,
            partie_terminee
        )

        pygame.display.flip()

        # Petite pause entre les tours.
        # Après la fin, on laisse le résultat visible.

        if partie_terminee:

            horloge.tick(30)

        else:

            horloge.tick(1000 // DELAI_TOUR if DELAI_TOUR > 0 else 60)

    pygame.quit()


# ============================================================
# 16. POINT D'ENTREE
# ============================================================

if __name__ == "__main__":

    main()
