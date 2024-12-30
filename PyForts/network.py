##################
# Network Module #
##################

import socket
import threading
import re

import pygame
from PyForts.events import EventHandler
import PyForts.console as console
from PyForts.enums import MessageTypes, Messages
import PyForts.settings as settings

import json


# global event_handler


class ClientNetwork:
    def __init__(self, server_ip, server_port):
        """
        Classe réseau conçue pour les joueurs.

        :param server_ip: Adresse IP du serveur.
        :type server_ip: str
        :param server_port: Port de connexion du serveur.
        :type server_port: int
        """
        # Définition des variables de base
        self.ip = server_ip
        self.port = server_port
        self.address = (self.ip, self.port)

        self.can_listen = True
        self.empty_messages = 0

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connexion au serveur
        self._server.connect(self.address)

    def send_message(self, message, message_code):
        """
        Permet d'envoyer un message au serveur.

        :param message: Message à envoyer.
        :type message: str
        :param message_code: Code du message à envoyer.
        :type message_code: Messages
        """
        conn = self._server
        send_message(conn, message, message_code)

    def receive_message(self):
        """
        Permet de recevoir un message du serveur.

        :returns: Tuple[Messages, str] --> Tuple[Code du message, contenu du message]
        """
        messages = receive_message(self._server)
        # Mesure de sécurité
        # On vérifie si le message reçu est nul. Au bout d'un certain nombre de messages vides, on déconnecte le client.
        if messages[0] is False:
            self.empty_messages += 1
        if self.empty_messages == 50:
            self.disconnect()
            console.printLog("Disconnected from server after receiving too many empty messages!", MessageTypes.WARNING)
        return messages

    def settimeout(self, seconds: int):
        """
        Indique un temps d'attente maximum pour un message.

        :param seconds:
        :return:
        """
        self._server.settimeout(seconds)

    def listen(self, event_handler):
        """
        Ecoute les messages reçus du serveur et génère un évènement PyGame USEREVENT correspondant au message reçu.

        :param event_handler: Gestionnaire des évènements.
        """
        while self.can_listen:
            messages = self.receive_message()
            for message in messages:
                if message[0] is not False:
                    event = pygame.event.Event(pygame.USEREVENT + message[0].value,
                                               {'conn': self._server, 'content': message[1]})
                    event_handler.handle(event)

    def disconnect(self):
        """
        Déconnecte le client du serveur.
        """
        self.can_listen = False
        self._server.close()


class ClientNetworkListenThread:
    def __init__(self, client_network: ClientNetwork, event_handler: EventHandler):
        """
        Remplace la fonction listen() de la classe ClientNetwork pour permettre au programme d'arrêter l'écoute dans le
        cas où il existe plusieurs threads actifs.

        Cette classe doit être lancée dans un thread séparé sans quoi le programme entrera dans une boucle infinie.

        :param client_network: Connexion au serveur.
        :type client_network: ClientNetwork
        :param event_handler: Gestionnaire d'évènements
        :type event_handler: EventHandler
        """
        self.client_network = client_network
        self.event_handler = event_handler

        self.can_listen = True

        self._listen_thread = threading.Thread(target=self._main)
        self._listen_thread.start()

    def _main(self):
        while self.can_listen:
            messages = self.client_network.receive_message()
            for message in messages:
                if message[0] is not False:
                    event = pygame.event.Event(pygame.USEREVENT + message[0].value,
                                               {'conn': self.client_network._server, 'content': message[1]})
                    self.event_handler.handle(event)

    def stop(self):
        """
        Arrête l'exécution du thread.
        """
        self.can_listen = False


class ServerNetwork:
    def __init__(self, server_port, server_ip=None):
        """
        Classe réseau conçue pour les serveurs.

        :param server_port: Port à utiliser par le serveur.
        :type server_port: int
        :param server_ip: Adresse IP du serveur. Si nulle, l'IP sera trouvée automatiquement.
        :type server_ip: str
        """

        self.server_port = server_port

        if server_ip is None:
            self.server_ip = socket.gethostbyname(socket.gethostname())
        else:
            self.server_ip = server_ip

        self.address = (self.server_ip, self.server_port)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server.bind(self.address)
        except OSError:
            console.printLog("Unable to bind this address to the server.", MessageTypes.ERROR)
            console.printLog("Please make sure you are allowed to use this address.", MessageTypes.ERROR)
            exit(0)

        self.is_running = True

    def start(self, function):
        """
        Démarre le serveur pour qu'il commence à accepter les connexions entrantes.\n
        Appelle la fonction `function` lorsqu'un nouveau client est connecté.\n
        Appelle la fonction avec `function(conn, addr)`, conn la connexion au client, et addr sont adresse.

        :param function: Fonction à appeler à la connexion d'un client.
        """
        # Accept incoming connections:
        self.server.listen()
        console.printLog(f"Server is listening on {self.address}.", [MessageTypes.INFO, MessageTypes.IMPORTANT])

        # Boucle pour accepter les nouvelles connexions.
        while self.is_running:
            conn, addr = self.server.accept()  # Wait for a new connection to the server.
            console.printLog(f"A new user has connected: {addr}.", MessageTypes.INFO)
            console.printLog(f"Started receiving messages from {addr}.", [MessageTypes.INFO, MessageTypes.SECONDARY])
            function(conn, addr)

    def stop(self):
        """
        Arrête le serveur pour qu'il n'accepte plus les connexions et les messages entrants, et n'envoie plus de
        messages.
        """
        console.printLog("Stopping server...", [MessageTypes.INFO, MessageTypes.IMPORTANT])
        self.is_running = False

    @staticmethod
    def send_message(player, message, message_code):
        """
        Envoie un message à un client.

        :param player: Joueur auquel envoyer le message.
        :type player: Player
        :param message: Message à envoyer.
        :type message: str
        :param message_code: Code du message à envoyer.
        :type message_code: Messages
        """
        conn = player.conn
        send_message(conn, message, message_code)

    @staticmethod
    def receive_message(player):
        """
        Reçoit un message venant d'un joueur.\n
        Peut être utilisé lorsqu'on attend un message précis à un moment donné.\n
        Poste un évènement PyGame avec le code du message, son contenu et les détails de connexion du joueur.

        :param player: Joueur duquel provient le message.
        :type player: Player
        """
        message_code, message_content = receive_message(player.conn)
        # Création de l'évènement pour prévenir le jeu de la réception du message.
        event = pygame.event.Event(pygame.USEREVENT + message_code.value, {'content': message_content})
        # On "publie" l'évènement.
        pygame.event.post(event)


def send_message(conn, message, message_code):
    """
    Permet d'envoyer un message à *conn*.

    :param conn: Connexion du destinataire.
    :type conn: socket
    :param message: Message à envoyer.
    :type message: str
    :param message_code: Code du message.
    :type message_code: Messages
    """
    if message_code is not None and message is not None:
        if type(message_code) is not int:
            # Si on n'a pas directement l'équivalent en entier du code du message, on le convertit :
            # (autrement dit, si on a juste Messages.PING, on fait Messages.PING.value)
            code_value = str(message_code.value)
        else:
            code_value = str(message_code - pygame.USEREVENT)
        message_sent = (' ' * (3 - len(code_value)) + str(code_value) + json.dumps(message))
        message_sent = re.sub(r'(\\)\1+', r'', message_sent)
        message_length = str(len(re.sub(r'(\\)\1+', r'', message_sent)))  # On enlève les \\' et \\\\\\ ...
        message_length += str(' ' * (4 - len(message_length)))

        conn.send((message_length + message_sent).encode(settings.FORMAT))
        console.printLog("Sent " + message_length + message_sent, [MessageTypes.INFO, MessageTypes.SECONDARY])
    else:
        console.printLog(f"Unable to send message to {conn.getsockname()} because message is incomplete!",
                         MessageTypes.WARNING)


def receive_message(conn):
    """
    Permet de recevoir un message de *conn*.

    :param conn: Connexion de l'envoyeur.
    :return: Liste des messages reçus. Si le message reçu est incorrect, retourne [(False, False)].
    """
    try:
        message_received = str(conn.recv(settings.HEADER_SIZE))  # On attend de recevoir un message.
    except OSError as ex:
        if ex.errno == 10038:
            return [(False, False)]
    except:
        console.printLog("Une erreur est survenue.", MessageTypes.ERROR)
        return [(False, False)]
    else:
        message_received = message_received[2:-1]  # On enlève le b' du début et le ' de la fin.
        if message_received:
            message_length = message_received[:4]
            # C'est peut être plusieurs messages en un.
            try:
                if int(message_length) <= len(re.sub(r'(\\)\1+', '', message_received[4:])):
                    messages = []
                    # Chargement de tous les messages
                    while len(message_received) > 0:
                        message_length = int(message_received[:4])
                        message = re.sub(r'(\\)\1+', '', message_received[4:])
                        message = message[:message_length]
                        code = Messages(int(message[:3]))
                        content = message[3:]
                        content = content[1:-1]  # Pour enlever les " des strings.
                        messages.append((code, content))
                        message_received = message_received[message_length+4:]

                        # On vérifie si le dernier bout du message est un message complet pour éviter les erreurs :
                        if message_received.strip():
                            try:
                                if int(message_received[:4]) > len(message_received[4:]):
                                    break
                            except ValueError:
                                # On n'a pas d'indication sur la longueur du message, donc il ne s'agit pas d'un
                                # nouveau message.
                                break

                    for message in messages:
                        console.printLog(f"Received message: {message}.", [MessageTypes.INFO, MessageTypes.SECONDARY])

                    return messages  # On retourne la liste des messages reçus.
                # Si on arrive ici, c'est que le message est vide, incomplet ou incorrect.
                console.printLog(f"Received incomplete/incorrect message from {conn.getsockname()}!", MessageTypes.ERROR)
                console.printLog(f"{message_received}", MessageTypes.ERROR)
            except ValueError:
                # int(message_length) n'a pas marché
                console.printLog("Skipped incorrect message.", MessageTypes.ERROR)
    return [(False, False)]


class Player:
    def __init__(self, conn, id, name="Connecting..."):
        """
        Classe réseau spéciale représentant un joueur connecté à un serveur.

        :param conn: Connexion (objet socket) au joueur.
        """
        self.conn = conn
        self.id = id
        self.name = name

        self.empty_messages = 0

        self.sent_first_ping = False

        self._running = True

    def send_message(self, message, message_code):
        """
        Envoie un message au joueur.

        :param message: Contenu du message.
        :param message_code: Code du message.
        :return:
        """
        send_message(self.conn, message, message_code)

    def receive_message(self):
        """
        Ecoute pour la réception d'un message du joueur.
        """
        return receive_message(self.conn)

    def listen(self, event_handler):
        """
        Ecoute continuellement les messages reçus depuis ce joueur.

        :return:
        """
        while self._running:
            messages = self.receive_message()
            for message in messages:
                console.printLog(f"received {message}", [MessageTypes.INFO, MessageTypes.SECONDARY])
                if message[0] is not False:
                    self.empty_messages = 0
                    event = pygame.event.Event(pygame.USEREVENT + message[0].value, {'conn': self.conn,
                                                                                     'content': message[1]})
                    event_handler.handle(event)
                else:
                    self.empty_messages += 1
                    # Au bout de 50 messages vides, on considère qu'on a perdu la connexion.
                    if self.empty_messages == 50:
                        console.printLog(f"Too many empty messages. Terminating connection with {self.conn}.",
                                         MessageTypes.WARNING)
                        event = pygame.event.Event(pygame.USEREVENT + Messages.DISCONNECT_PLAYER.value,
                                                   {'conn': self.conn})
                        event_handler.handle(event)
                        self.disconnect()

    def disconnect(self):
        """
        Déconnecte le serveur du client.
        """
        self._running = False
        self.conn.close()
