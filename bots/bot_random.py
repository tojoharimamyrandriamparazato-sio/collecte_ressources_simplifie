
# bot_random.py

import random


def decide(observation):

    actions = [
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT",
        "COLLECT",
        "WAIT"
    ]

    # Si le sac est plein, rentrer à la base
    if len(observation["mon_sac"]) >= observation["capacite_sac"]:

        return random.choice([
            "UP", "DOWN", "LEFT", "RIGHT"
        ])

    return random.choice(actions)
