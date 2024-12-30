#######################
# CONSOLE INTERACTION #
#######################

from PyForts.enums import LogColors, MessageTypes
import threading
from datetime import datetime


_screenlock = threading.Semaphore(value=1)


def printLog(message, decorations):
    """
    Afficher un message dans la console.

    :param message: Message à afficher.
    :type message: str
    :param decorations: Couleur / Type du message à afficher (information, avertissement, erreur, etc.).
    :type decorations: list[MessageTypes]
    """
    _screenlock.acquire()

    # On a besoin que decorations soit itérable, donc on en fait une liste.
    if type(decorations) is not list:
        decorations = [decorations]

    # Affichage de l'heure
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    timestamp += ''.join(' '*i for i in range(10-len(timestamp)))  # Afficher la date sur 10 caractères.
    timestamp = LogColors.SECONDARY + timestamp + LogColors.ENDC

    # Type du message
    message_type = ""
    message_color = ""
    if MessageTypes.INFO in decorations:
        message_type = "[INFO]    "

        # Decoration du message, uniquement si c'est une info.
        if MessageTypes.SECONDARY in decorations:
            message_color = LogColors.SECONDARY
        elif MessageTypes.IMPORTANT in decorations:
            message_color = LogColors.HEADER
    elif MessageTypes.WARNING in decorations:
        message_type = LogColors.WARNING + "[WARNING] "
    elif MessageTypes.ERROR in decorations:
        message_type = LogColors.FAIL + "[ERROR]   "

    if message_type == "":
        _screenlock.release()
        printLog("Tried displaying the following message without decorations: " + message, [MessageTypes.WARNING])
        return

    # Affichage du message
    print(timestamp, message_color + message_type, message + LogColors.ENDC)

    _screenlock.release()


def question(message, decorations):
    """
    Permet de poser une question à l'utilisateur.

    :param message: Question à poser à l'utilisateur.
    :param decorations: Couleur / Type du message à afficher (information, avertissement, erreur, etc.).
    :type decorations: MessageTypes
    :return: True si l'utilisateur répond oui, False sinon.
    """
    printLog(message + " ([y/Y] Yes ; [n/N] No) : ", decorations)
    answer = input()
    return answer == "y" or answer == "Y"  # On retourne Vrai si l'utiliateur entre y ou Y, sinon Faux.
