##############################
# CONSTANTES ET ENUMERATIONS #
##############################

from enum import Enum


class TextInput_Type(Enum):
    """
    Constantes de type d'entrée pour les champs d'entrée.
    """
    INTEGER = 0x1
    """
    N'accepte que des chiffres et des numéros.
    """
    FLOAT = 0x2
    """
    N'accepte que des chiffres et des numéros séparés par des virgules.\n
    Attention : plusieurs virgules pourraient être saisies.
    """
    ADDRESS = INTEGER_WITH_DOTS = 0x3
    """
    N'accepte que des chiffres et des numéros séparés de points.
    """
    TEXT = 0x4
    """
    Texte brut dans le quel tous les caractères sont acceptés hormis Echap, Entrée, Suppr et Retour.
    """


class Alignments(Enum):
    """
    Constantes d'alignement.
    """
    TOP_LEFT = 0x1
    """
    Alignement en haut à gauche.
    """
    TOP_CENTER = 0x2
    """
    Alignement en haut au centre.
    """
    TOP_RIGHT = 0x3
    """
    Alignement en haut à droite.
    """
    CENTER_LEFT = 0x4
    """
    Alignement au centre à gauche.
    """
    CENTER = 0x5
    """
    Alignement au centre.
    """
    CENTER_RIGHT = 0x6
    """
    Alignement au centre à droite.
    """
    BOTTOM_LEFT = 0x7
    """
    Alignement en bas à gauche.
    """
    BOTTOM_CENTER = 0x8
    """
    Alignement en bas au centre.
    """
    BOTTOM_RIGHT = 0x9
    """
    Alignement en bas à droite.
    """


class Messages(Enum):
    """
    Contient tous les messages envoyés entre le client et le serveur.
    """

    # STATUT DES JOUEURS / PARTIE
    PING = 0x01
    """
    Ping envoyé au serveur / client.
    Lors du premier ping, le serveur indique au client s'il peut être un joueur.
    """
    DISCONNECT_PLAYER = 0x02
    """
    Le client indique au serveur sa déconnexion volontaire.
    """
    DISCONNECT_PLAYERS = 0x03
    """
    Le serveur indique la fin de la partie aux joueurs et leur déconnexion imminente.
    """
    GAME_PAUSE = 0x04
    """
    Le serveur indique au client que la partie est en pause.
    """
    GAME_RESUME = 0x05
    """
    Le serveur indique au client que la partie a reprie.
    """
    GAME_START = 0x06
    """
    Le serveur démarre la partie et en informe les clients.
    """

    # CONSTRUCTION DE BASES
    UPDATE_PLAYER1_BASE_CONSTRUCTION = 0x11
    """
    Le joueur 1 (client) envoie au serveur sa nouvelle base (plan 0 construction).
    """
    UPDATE_PLAYER1_BASE_WEAPONS = 0x12
    """
    Le joueur 1 (client) envoie au serveur sa nouvelle base (plan 1 armes).
    """
    UPDATE_PLAYER2_BASE_CONSTRUCTION = 0x13
    """
    Le joueur 2 (client) envoie au serveur sa nouvelle base (plan 0 construction).
    """
    UPDATE_PLAYER2_BASE_WEAPONS = 0x14
    """
    Le joueur 2 (client) envoie au serveur sa nouvelle base (plan 1 armes).
    """
    UPDATE_PLAYER1_BASE_MINES = 0x15
    """
    Le joueur 1 (client) envoie au serveur sa nouvelle base (plan mines).
    """
    UPDATE_PLAYER2_BASE_MINES = 0x16
    """
    Le joueur 2 (client) envoie au serveur sa nouvelle base (plan mines).
    """
    REACTOR_DEAD = 0x17
    """
    Le joueur signal au serveur que son réacteur est détruit.
    """
    UPDATE_PLAYER_BASE_CONSTRUCTION = 0x1F
    """
    La base du joueur a été mise à jour.\n
    Ce type de message peut être utilisé lorsqu'un projectile détruit une partie de la base du joueur. 
    
    Remarque : Seulement utilisé côté client. Ce message n'est jamais envoyé au serveur. 
    """

    # PROJECTILES ET ARMES
    NEW_PROJECTILE = 0x21
    """
    Le client indique au serveur la création d'un nouveau projectile.
    """

    # Connexion des joueurs
    ASK_PLAYER = 0x31
    """
    Le client demande au serveur s'il peut être un joueur.
    """
    ASK_SPECTATOR = 0x32
    """
    Le client demande au serveur s'il peut être un spectateur.
    """
    PLAYER_LIST = 0x33
    """
    Le serveur envoie aux clients la liste des joueurs et leurs rôles.
    """


class Colors:
    WHITE = (255, 255, 255)

    BLACK = (0, 0, 0)

    RED_BRIGHT = (255, 0, 0)
    RED_SALMON = (249, 65, 68)
    RED_DARK = (111, 29, 27)

    GREEN_BRIGHT = (0, 255, 0)
    GREEN_LIGHT = (144, 255, 85)
    GREEN = (79, 119, 45)
    DARK_GREEN = (49, 87, 44)
    DARKER_GREEN = (19, 42, 19)

    BLUE_BRIGHT = (0, 0, 255)
    DARK_BLUE = (39, 68, 114)
    BLUE_MIDNIGHT = (65, 114, 159)
    BLUE = (96, 168, 235)

    LIGHT_GRAY = (201, 201, 201)
    DARK_GRAY = (59, 59, 59)
    DARKER_GRAY = (43, 43, 43)

    BROWN_DARK = (67, 40, 24)
    BROWN = (153, 88, 42)

    BEIGE_LIGHT = (255, 230, 167)
    BEIGE_DARK = (187, 148, 87)


class LogColors:
    """
    Couleurs utilisées dans le terminal pour afficher des informations lors de l'exécution du serveur.
    """
    HEADER = '\033[95m'
    """
    Pour les messages importants qui ne sont pas des erreurs.
    """
    SECONDARY = '\033[90m'
    """
    Couleur grise, pour les messages secondaires.
    """
    WARNING = '\033[93m'
    """
    Couleur jaune, pour les messages nécessitant l'attention de l'utilisatuer.
    """
    FAIL = '\033[91m'
    """
    Couleur rouge, pour les erreurs.
    """
    ENDC = '\033[0m'
    """
    Réinitialise la couleur.
    """


class MessageTypes:
    """
    Types de messages possibles pour la console.
    """
    NORMAL = CLASSIC = STANDARD = 0x0
    """
    Message standard sans importance particulière.
    """
    INFO = 0x1
    """
    Message d'information.
    """
    WARNING = 0x2
    """
    Message d'avertissement.
    """
    ERROR = 0x3
    """
    Message d'erreur.
    """
    IMPORTANT = 0x4
    """
    Message important.
    """
    SECONDARY = 0x5
    """
    Message secondaire.
    """


class ScaleMode(Enum):
    STRETCH = 0x1
    """
    Etire l'image pour la faire rentrer dans une surface.
    """
    COVER = 0x2
    """
    Agrandit l'image jusqu'à ce qu'elle occupe toute une surface sans étirement.
    """
    TILE_HORIZONTAL_COVER = 0x3
    """
    Agrandit l'image jusqu'à ce qu'elle occupe tout l'espace vertical et la répète horizontalement.
    """
