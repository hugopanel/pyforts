##################
# PYFORTS MODULE #
##################

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from PyForts.enums import LogColors


PROJECT_NAME = "PyForts"
PROJECT_DESCRIPTION = "Construisez votre fort, défendez-le et éliminez la menace dans ce jeu de stratégie inspiré du " \
                      "jeu Forts."
AUTHOR = "Groupe 41"
AUTHORS = ["Evan ZANZUCCHI", "Hugo PANEL", "Mohamed ZAMMIT CHATTI", "Nathan MOREL", "Victor BOULET"]
COPYRIGHT = f"Copyright (c) 2020-2021 {', '.join(author for author in AUTHORS)}."
VERSION = 1.0
BUILD = 230521

print(LogColors.SECONDARY, end='')  # Couleur texte secondaire
print("Loaded PyForts library.")
print(f"Using {PROJECT_NAME} version {VERSION}, build b{BUILD}.")
print(COPYRIGHT)
print(LogColors.ENDC)  # Réinitialisation de la couleur
