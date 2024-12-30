##################
# PYFORTS SERVER #
##################

"""
Copyright (c) 2021, Evan ZANZUCCHI, Hugo PANEL, Mohamed ZAMMIT CHATTI, Nathan MOREL, Victor BOULET.

Vous pouvez lancer ce serveur depuis le terminal.

> python3 server.py <args>

Arguments acceptés (agruments optionnels) :
-p <port> | --port <port> : Spécifie le port à utiliser par le serveur.
-i <address> | --ip <address> : Spécifie l'adresse IP à utiliser par le serveur. L'adresse IP doit être accessible.
-v | -V | --verbose | --VERBOSE : Activer le mode "verbose". Le mode verbose affiche les messages moins importants à
                                    l'écran.
"""

import threading
import sys
import socket
import signal
import sys

import PyForts.console as console
import PyForts.network as net
from PyForts.enums import MessageTypes, Messages
from PyForts.events import EventHandler

import pygame


# ---- Vous pouvez modifier ces variables pour ne pas avoir à préciser ip/port à chaque démarrage du serveur.
SERVER_IP = None  # Adresse IP utilisée par le serveur.
SERVER_PORT = 4408  # Port utilisé par le serveur.

# TODO: Déplacer ces variables dans un fichier de configuration propre au serveur.
# TODO: Vérifier les mods des clients et les comparer à ceux du serveur.

thread_network = None

VERBOSE = False

event_handler = EventHandler()

games = []

total_players = 0


# Arrêt du serveur par CTRL+C
def signal_handler(signal, frame):
    console.printLog("Stopping server on user's request...", [MessageTypes.INFO, MessageTypes.IMPORTANT])
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def newPlayer(conn, addr):
    if VERBOSE:
        console.printLog("New user connected.", [MessageTypes.INFO, MessageTypes.SECONDARY])

    global total_players
    total_players += 1
    player = net.Player(conn, total_players)

    # On crée une nouvelle partie s'il n'y en n'a pas déjà.
    if not games:
        games.append(Game())
    # Et on y ajoute le joueur
    games[-1].player_list.append(player)
    games[-1].waiting.append(player)

    # On crée un nouveau thread pour recevoir des messages de ce joueur en continu.
    thread_listen = threading.Thread(target=player.listen, args=(event_handler,))
    thread_listen.start()


class Game:
    def __init__(self):
        self.alive = True
        self.started = False

        # On a trois états (rôles) possibles pour l'utilisateur : Joueur, spectateur, et en attente.
        # Une quatrième liste (self.player_list) regroupe tous les clients, peu importe leur rôle.
        self.waiting = []
        self.spectators = []
        self.players = []
        self.player_list = []

        # On associe les évènements qui nous intéressent.
        event_handler.bind_event(pygame.USEREVENT + Messages.PING.value, self.handle_ping)
        event_handler.bind_event(pygame.USEREVENT + Messages.DISCONNECT_PLAYER.value, self.handle_disconnections)
        event_handler.bind_event(pygame.USEREVENT + Messages.ASK_PLAYER.value, self.handle_ask_player)
        event_handler.bind_event(pygame.USEREVENT + Messages.ASK_SPECTATOR.value, self.handle_ask_spectator)
        event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_CONSTRUCTION.value,
                                 self.handle_player_base_update)
        event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_CONSTRUCTION.value,
                                 self.handle_player_base_update)
        event_handler.bind_event(pygame.USEREVENT + Messages.NEW_PROJECTILE.value,
                                 self.handle_new_projectile)
        event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_WEAPONS.value,
                                 self.handle_player_weapons_update)
        event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_WEAPONS.value,
                                 self.handle_player_weapons_update)
        event_handler.bind_event(pygame.USEREVENT + Messages.REACTOR_DEAD.value,
                                 self.handle_reactor_dead)
        event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_MINES.value,
                                 self.handle_player_mines_update)
        event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_MINES.value,
                                 self.handle_player_mines_update)

        lobby_thread = threading.Thread(target=self.lobby)
        lobby_thread.start()

    def lobby(self):
        console.printLog("Started Lobby", [MessageTypes.INFO, MessageTypes.IMPORTANT])
        while len(self.players) < 2:
            pass
        self.game()

    def handle_ping(self, args):
        if self.alive:
            # On vérifie si le joueur est dans cette partie.
            # Trouver le joueur avec cette connexion.
            player = next((player for player in self.waiting if player.conn == args['conn']), None)
            player: net.Player
            # if player in self.waiting:
            if player in self.player_list:
                # On vérifie si c'est le premier ping du joueur
                if not player.sent_first_ping:
                    # C'est son premier ping
                    # On sauvegarde son nom.
                    player.name = args['content']
                    console.printLog(f"Player {args['conn']} is now named '{player.name}.'", MessageTypes.INFO)
                    if not self.started:
                        player.send_message("1", Messages.PING)
                    else:
                        player.send_message("0", Messages.PING)
                    self.send_player_list()
            else:
                console.printLog(f"Player {args['conn']} not in player base", MessageTypes.ERROR)

    def handle_disconnections(self, args):
        if self.alive:
            player = get_player(args['conn'])
            player: net.Player  # Indication pour l'IDE.
            console.printLog(f"Closing connection with player {player.name}.", MessageTypes.INFO)

            if player in self.players:
                self.players.remove(player)
            if player in self.spectators:
                self.spectators.remove(player)
            if player in self.waiting:
                self.waiting.remove(player)

            self.player_list.remove(player)

            player.disconnect()

            if not self.started:
                self.send_player_list()
            else:
                if len(self.players) < 2:
                    self.stop_game(2)

    def handle_ask_player(self, args):
        if self.alive:
            player = get_player(args['conn'])
            if len(self.players) < 2:
                # On vérifie si le joueur se trouve dans les spectateurs ou la liste d'attente
                if player in self.spectators:
                    self.spectators.remove(player)
                if player in self.waiting:
                    self.waiting.remove(player)
                # On l'ajoute à la liste des joueurs
                if player not in self.players:
                    self.players.append(player)
                player.send_message("1", Messages.ASK_PLAYER)
                self.send_player_list()
            else:
                player: net.Player
                player.send_message("0", Messages.ASK_PLAYER)

    def handle_ask_spectator(self, args):
        if self.alive:
            player = get_player(args['conn'])
            # On vérifie si le joueur est déjà dans les joueurs ou dans la liste d'attente
            if player in self.players:
                self.players.remove(player)
            if player in self.waiting:
                self.waiting.remove(player)
            # Alors on l'ajoute
            if player not in self.spectators:
                self.spectators.append(player)
            player.send_message("1", Messages.ASK_SPECTATOR)
            self.send_player_list()

    def handle_new_projectile(self, args):
        if self.alive:
            # On récupère l'autre joueur
            other_player = next((player for player in games[-1].players if player.conn != args['conn']), None)
            if other_player is None:
                console.printLog("Unable to send new projectile to opposite player!", MessageTypes.ERROR)
            else:
                other_player: net.Player
                other_player.send_message(args['content'], Messages.NEW_PROJECTILE)

    def handle_player_mines_update(self, args):
        if self.alive:
            # On récupère l'autre joueur
            other_player = next((player for player in games[-1].players if player.conn != args['conn']), None)
            if other_player is None:
                console.printLog("Unable to send new mines to opposite player!", MessageTypes.ERROR)
            else:
                other_player: net.Player
                other_player.send_message(args['content'], args['event_type'])

    def send_player_list(self):
        if self.alive:
            player_list = []

            for player in self.players:
                player_list.append(player.name + " (Joueur)")

            for player in self.spectators:
                player_list.append(player.name + " (Spectateur)")

            for player in self.waiting:
                player_list.append(player.name)

            # On envoie la liste à chaque joueur.
            for player in self.player_list:
                player.send_message(player_list, Messages.PLAYER_LIST)

    def handle_player_base_update(self, args):
        if self.alive:
            if args["event_type"] == pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_CONSTRUCTION.value:
                player_to_send_to = self.players[1]
            else:
                player_to_send_to = self.players[0]

            if player_to_send_to is not None:  # Mesure de sécurité.
                player_to_send_to: net.Player
                player_to_send_to.send_message(args["content"], args["event_type"])

    def handle_player_weapons_update(self, args):
        if self.alive:
            if args['event_type'] == pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_WEAPONS.value:
                player_to_send_to = self.players[1]
            else:
                player_to_send_to = self.players[0]

            player_to_send_to.send_message(args["content"], args["event_type"])

    def handle_reactor_dead(self, args):
        if self.alive:
            winner = int(args['content'])
            # C'est le joueur qui perd qui envoie le message, donc on doit inverser les numéros de joueur :
            winner = 0 if winner == 1 else 1
            self.stop_game(winner)

    def stop_game(self, exit_code):
        # On demande aux joueurs de se déconnecter
        self.started = False
        self.alive = False
        for player in self.player_list:
            player.send_message(str(exit_code), Messages.DISCONNECT_PLAYERS)
            console.printLog(f"Closing connection with player {player.name}.", MessageTypes.INFO)
            player.disconnect()
        # On supprime les joueurs de la partie.
        self.players.clear()
        self.spectators.clear()
        self.waiting.clear()
        self.player_list.clear()
        # La partie est arrêtée.
        games.remove(self)
        console.printLog("Stopped Game.", [MessageTypes.INFO, MessageTypes.IMPORTANT])

    def game(self):
        if self.alive:
            console.printLog("Started new Game", [MessageTypes.INFO, MessageTypes.IMPORTANT])
            self.started = True
            # Send START GAME Message
            player_number = 0
            for player in self.player_list:
                player.send_message(str(player_number), Messages.GAME_START)
                if player in self.players:
                    player_number += 1


def get_player(conn):
    player = next((player for player in games[-1].players if player.conn == conn), None)
    if not player:
        player = next((player for player in games[-1].spectators if player.conn == conn), None)
        if not player:
            player = next((player for player in games[-1].waiting if player.conn == conn), None)
    return player


if __name__ == "__main__":
    console.printLog("== PYFORTS  SERVER ==", [MessageTypes.INFO, MessageTypes.IMPORTANT])
    # Arguments de lancement
    i = 0
    while i < len(sys.argv):
        argument = sys.argv[i]
        # Port
        if argument == "-p" or argument == "--port":
            console.printLog(f"Now using port {sys.argv[i+1]}.", MessageTypes.WARNING)
            try:
                SERVER_PORT = int(sys.argv[i+1])
            except ValueError:
                console.printLog("The specified port cannot be used.", MessageTypes.ERROR)
                if not console.question(f"Continue and use the default port ({SERVER_PORT}) ?",
                                    MessageTypes.ERROR):
                    exit(0)
            i += 1  # On augmente de 1 pour passer l'argument suivant.
        # IP
        if argument == "-i" or argument == "--ip":
            console.printLog(f"Now using address {sys.argv[i+1]}.", MessageTypes.WARNING)
            SERVER_IP = sys.argv[i+1]
            i += 1
        # Verbose
        if argument == "-v" or argument == "-V" or argument == "--verbose" or argument == "--VERBOSE":
            VERBOSE = True
            console.printLog("Verbose mode enabled.", MessageTypes.WARNING)

        i += 1  # Ici on incrémente juste i normalement, vu que c'est une boucle while.

    console.printLog("Server is starting...", MessageTypes.INFO)

    # Création du serveur
    network = net.ServerNetwork(SERVER_PORT, SERVER_IP)

    # Démarrage du serveur
    thread_network = threading.Thread(target=network.start, args=[newPlayer])
    thread_network.daemon = True
    # On crée un thread pour la fonction network.start() qui accepte les nouvelles connexions en continu.
    # network.start() appelle la fonction newPlayer() pour gérer chaque nouvelle connexion.
    thread_network.start()

    while True:
        # On garde le thread principal en vie pour ne pas tuer les autres threads dès le début.
        # Comme ça, si l'utilisateur fait CTRL+C pour quitter le serveur, le thread principal se fermera (puisqu'il est
        # toujours en vie) et fermera les autres threads avec (puisque ce sont des daemons).
        pass
