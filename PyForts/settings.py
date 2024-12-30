############################
# GAME SETTINGS MANAGEMENT #
############################

import json

import PyForts.console as console
from PyForts.enums import MessageTypes


#---- PARAMETRES PROTEGES :
# Un avertissement doit être affiché si ces paramètres sont modifiés.
HEADER_SIZE = 4096  # Ne doit pas être modifié par le joueur s'il rejoint des serveurs officiels.
"""
Taille max. des messages envoyés/reçus. \n
**Ne devrait pas être modifié.**
"""
FORMAT = 'utf-8'  # Ne doit pas être modifié par le joueur.
"""
Format d'encodage des messages envoyés/reçus. \n
**Ne devrait pas être modifié.**
"""

IS_MODDED = False  # Defined at runtime
"""
Si le client est moddé, il envoie cette variable au serveur qui peut alors accepter ou refuser la connexion.\n
Cette variable est définie pendant l'exécution du jeu.
"""

mods_list = []  # Defined at runtime
"""
Contient la liste de tous les mods chargés.\n
Cette liste est transmise aux serveurs auxquels se connecte l'utilisateur.
"""


#---- FONCTIONS :
settings_file_path = "settings.json"

# Chargement des paramètres dans l'objet settings
settings = None
try:
    with open(settings_file_path, "r", encoding=FORMAT) as _settings:
        _settings = _settings.readlines()
        if len(_settings) > 1:
            # On convertit en string en enlevant les retours à la ligne :
            _settings = ''.join(i[:-1] if i[-1] == '\n' else i for i in _settings)
        else:
            _settings = _settings[0]  # Conversion en string
        try:
            settings = json.loads(_settings)
        except:
            console.printLog("The settings file uses an incorrect JSON format!", MessageTypes.ERROR)
            exit(0)
except IOError:
    console.printLog("Unable to find settings file!", MessageTypes.ERROR)
    exit(0)


def saveSettings():
    """
    Sauvegarde les paramètres dans le fichier de configuration.
    """
    content = json.dumps(settings, ensure_ascii=False, indent=2)
    try:
        with open(settings_file_path, "w", encoding=FORMAT) as file:
            file.write(content)


    except IOError:
        console.printLog("Unable to save settings!", MessageTypes.ERROR)


USERNAME = settings["profile"]["username"]
"""
Nom d'utilisateur du joueur.
"""
