#############################
# PYFORTS CLIENT GAME LOGIC #
#############################

"""
game.py

Copyright (c) 2021 :
Hugo PANEL, Nathan MOREL, Mohamed ZAMMIT CHATTI, Victor BOULET, Evan ZANZUCCHI
"""

import random

import PyForts
import PyForts.console as console
import mods.base_content.base_content
from PyForts.enums import *

if __name__ == "__main__":
    console.printLog("Please, launch client.py instead!", MessageTypes.ERROR)
    console.printLog("Veuillez lancer client.py à la place !", MessageTypes.ERROR)
    exit(0)

import PyForts.gui as gui
from PyForts.gui import window, window_width, window_height, window_fps
from PyForts.settings import *
from PyForts.weapon import weapons
import PyForts.network as net
from PyForts.events import EventHandler
from PyForts.math import Vec2d

import os
import socket
import threading
import math
import json

import pygame


class Game:
    def __init__(self, server_ip, server_port, username):
        """
        Logique du jeu, pendant le lobby, la partie, et après la victoire / défaite.

        :param server_ip: Adresse IP du serveur.
        :param server_port: Port du serveur.
        :param username: Nom d'utilisateur du joueur.
        """

        # ----- LOBBY:
        self.ip = server_ip
        self.port = int(server_port)
        self.username = username
        self.server = None

        self.buttons = None

        self.event_handler = EventHandler()

        # self.running = True
        self.lobby_running = False
        self.game_running = False
        self.launch_game = False

        # ----- GAME:
        self.server = None
        # self.server = server_connection
        self.player_number = None
        # self.player_number = player_number

        self.current_plane = 0  # On ne garde qu'un seul plan pour l'instant puisqu'on n'a pas encore fait ce qui est
        # nécessaire pour relier les planches.

        self.grid_tile_size = 20  # Taille de chaque carreau de la grille.
        self.player1_grid = {
            "x": 30, "y": 25,  # Position de la grille (x, y) en pixels.
            "width": 15, "height": 11  # Taille de la grille (width, height) en carreaux.
        }
        self.player2_grid = {
            "x": 30, "y": 25,  # Position de la grille (x, y) en pixels.
            "width": 15, "height": 11  # Taille de la grille (width, height) en carreaux.
        }

        self.INVENTORY_HEIGHT = 70  # Constante, taille en pixels de l'inventaire.

        # Coordonées de la grille :
        # ------2------
        # |           |
        # 0           1
        # |           |
        # ------3------
        # Coordonnées y dans le sens de pygame, du haut vers le bas.
        # @---> +x
        # |
        # V
        # +y
        self.player1_grid_coordinates = (
            self.player1_grid["x"],
            self.player1_grid["x"] + self.player1_grid["width"] * self.grid_tile_size,
            window_height - (self.INVENTORY_HEIGHT + self.player1_grid["y"] + (self.player1_grid["height"]) *
                             self.grid_tile_size),
            window_height - (self.INVENTORY_HEIGHT + self.player1_grid["y"])
        )

        self.player2_grid_coordinates = (
            window_width - (self.player2_grid["x"] + self.player2_grid["width"] * self.grid_tile_size),
            window_width - (self.player2_grid["x"]),
            window_height - (self.INVENTORY_HEIGHT + self.player2_grid["y"] + (self.player2_grid["height"]) *
                             self.grid_tile_size),
            window_height - (self.INVENTORY_HEIGHT + self.player2_grid["y"])
        )

        self.points_group = pygame.sprite.Group()

        self.player1_weapons = pygame.sprite.Group()  # Contient les images des armes uniquement, aucune classe Weapon !
        self.player1_weapons_group = []  # Contient les classes Weapon directement.
        self.player2_weapons = pygame.sprite.Group()
        self.player2_weapons_group = []
        self.player1_projectiles_group = []
        self.player2_projectiles_group = []
        self.player1_construction_plane = pygame.sprite.Group()
        self.player2_construction_plane = pygame.sprite.Group()
        self.player1_mines_plane = pygame.sprite.Group()
        self.player2_mines_plane = pygame.sprite.Group()

        # Ressources du joueur
        self.player_resources = 100  # Ressources disponibles du joueur
        self.player_default_rps = 10  # Ressources par seconde que gagne le joueur par défaut.
        self.player_rps = self.player_default_rps  # Ressources par seconde que gagne le joueur.
        self.player_max_resources = 200  # Ressources maximum par joueur.

        self.wall_price = 5

        self.mine_rps_increase = 12
        self.mine_cost = 200
        self.mine_max_number = 2

        self.buttons = []

        self.event_handler = EventHandler()
        self.listen_thread = None

        self.exit_code = None

    def connect(self):
        # Affichage de l'écran de connexion
        background = gui.Background(os.path.join('assets', 'main_menu_background.png'), Alignments.CENTER,
                                    ScaleMode.COVER)
        logo = gui.Image(os.path.join('assets', 'pyforts_logo.png'), (gui.window_width // 2, 130),
                         (1681 // 2, 339 // 2))
        status_label = gui.Button(0, "[1] Connexion au serveur en cours...", (10, window_height // 2 - 70 // 2),
                                  (gui.window_width - 20, 70),
                                  Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40)
        status_label.disabled = True

        window.blit(background.image, background.rect)
        window.blit(logo.image, logo.rect)
        status_label.draw()

        pygame.display.update()

        # Initialisation et connexion au serveur.
        success = False
        messages = None
        try:
            self.server = net.ClientNetwork(self.ip, self.port)
            success = True
            status_label.text = "[2] Connexion établie. Récupération d'informations..."
            status_label.background_color = Colors.DARK_GREEN
            status_label.draw()
            pygame.display.update()
        except TimeoutError:
            status_label.text = "[1] Le serveur ne répond pas."
        except ConnectionRefusedError:
            status_label.text = "[1] Le serveur n'accepte pas de connexions."

        # On vérifie que la connexion se soit bien faite :
        if self.server is None:
            status_label.text = "[1] La connexion a échouée."
            success = False

        if success:
            # Envoi du premier ping.
            try:
                self.server.settimeout(5)  # On donne 5 secondes au serveur pour répondre au PING.
                self.server.send_message(self.username, Messages.PING)
                messages = self.server.receive_message()
            except (TimeoutError, socket.timeout):
                status_label.text = "[2] Le serveur a mis trop de temps à répondre à la demande."
                success = False
                self.server.send_message("0", Messages.DISCONNECT_PLAYER)
            except ConnectionResetError:
                status_label.text = "[2] Le serveur a quitté inopinément."
                success = False
                self.server.send_message("0", Messages.DISCONNECT_PLAYER)
            self.server.settimeout(0)

        # Si on arrive ici, c'est qu'on est connecté !
        # Pas besoin de se soucier de la variable messages non référencée car elle le sera forcément.
        if messages:
            ping_message = next((message for message in messages if message[0] == Messages.PING), None)
            if ping_message is None:
                success = False
                status_label.text = "[2] La connexion au serveur a été rompue."
            else:
                if ping_message[1] == "1":
                    # On continue
                    status_label.text = "[2] Connexion acceptée !"
                    status_label.background_color = Colors.DARK_GREEN
                    status_label.draw()
                    pygame.display.update()
                    # On attend un certain nombre de temps, pour ne pas avoir trop de flashs à l'écran. Le message
                    # doit rester affiché suffisamment de temps pour que l'utilisateur puisse le lire.
                    pygame.time.delay(1500)
                    self.lobby()
                    while self.lobby_running or self.game_running:
                        pass
                    return
                else:
                    success = False
                    status_label.text = "[2] La partie est déjà en cours et n'accepte plus de connexions."

        if not success:
            running = True
            status_label.background_color = Colors.RED_DARK
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        exit()
                    if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                        running = False
                status_label.draw()
                pygame.display.update()
            return

    def lobby(self):
        background = gui.Background(os.path.join('assets', 'main_menu_background_blurred.png'),
                                    Alignments.CENTER, ScaleMode.COVER)

        self.buttons = [
            gui.Button(0, "Quitter le serveur", (10, 10), (gui.window_width - 20, 70),
                       Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40),
            gui.Label(1, "Rôle :", (10, 100), (gui.window_width - 20, 70), Alignments.CENTER_LEFT,
                      Colors.LIGHT_GRAY, "default", 40),
            gui.Button(2, "Joueur", (10, 150), (gui.window_width - (gui.window_width // 2) - 20, 70),
                       Colors.LIGHT_GRAY, Colors.BLUE_MIDNIGHT, "default", 40),
            gui.Button(3, "Spectateur", (gui.window_width // 2 + 10, 150),
                       (gui.window_width - (gui.window_width // 2) - 20, 70),
                       Colors.LIGHT_GRAY, Colors.GREEN, "default", 40),
            gui.Label(4, "Liste des joueurs :", (10, 320), (gui.window_width - 20, 70), Alignments.CENTER_LEFT,
                      Colors.LIGHT_GRAY, "default", 40),
            gui.List(5, [], (10, 370), (), empty_message="Une erreur est survenue lors de l'affichage.", offset=40)
        ]

        # On écoute les messages reçus :
        self.event_handler.bind_event(pygame.USEREVENT + Messages.PLAYER_LIST.value, self.update_player_list)
        self.event_handler.bind_event(pygame.USEREVENT + Messages.GAME_START.value, self.start_game)

        self.listen_thread = net.ClientNetworkListenThread(self.server, self.event_handler)

        self.lobby_running = True
        try:
            while self.lobby_running:
                # Update window
                window.blit(background.image, background.rect)
                for button in self.buttons:
                    button.draw()

                # Events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # running = False
                        exit()
                    if event.type == pygame.MOUSEBUTTONUP:
                        for button in self.buttons:
                            if type(button) is gui.Button:
                                if button.click(pygame.mouse.get_pos()):
                                    if button.id == 0:
                                        self.server.send_message("", Messages.DISCONNECT_PLAYER)
                                        self.lobby_running = False
                                        # running = False
                                    if button.id == 2:
                                        self.server.send_message("", Messages.ASK_PLAYER)
                                    if button.id == 3:
                                        self.server.send_message("", Messages.ASK_SPECTATOR)

                pygame.display.update()

                if self.launch_game is not False:
                    # C'est un contournement pas beau, mais pour le moment on est obligé, puisque seul le thread
                    # principal peut dessiner à l'écran et utiliser les autres fonctions essentielles de pygame.
                    # Donc comme ça, on appelle la fonction du jeu depuis le thread principal, et pas l'event_handler.
                    self.main(self.launch_game)
                    return
        except (ConnectionResetError, ConnectionAbortedError):
            waiting = True
            background = gui.Background(os.path.join('assets', 'main_menu_background.png'), Alignments.CENTER,
                                        ScaleMode.COVER)
            logo = gui.Image(os.path.join('assets', 'pyforts_logo.png'), (gui.window_width // 2, 130),
                             (1681 // 2, 339 // 2))
            status_label = gui.Button(0, "Le serveur a quitté inopinément.", (10, window_height // 2 - 70 // 2),
                                      (gui.window_width - 20, 70),
                                      Colors.LIGHT_GRAY, Colors.RED_DARK, "default", 40)
            status_label.disabled = True

            self.game_running = False

            window.blit(background.image, background.rect)
            window.blit(logo.image, logo.rect)
            status_label.draw()
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        exit()
                    if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                        waiting = False
                pygame.display.update()
        while self.game_running:
            pass

        # On arrête le thread d'écoute de messages si on quitte le lobby.
        self.listen_thread.stop()
        return False

    def start_game(self, args):
        self.lobby_running = False
        self.launch_game = args
        self.game_running = True

    def update_player_list(self, args):
        try:
            player_list = self.buttons[5]
        except IndexError:
            console.printLog("Outdated function.", MessageTypes.WARNING)
        else:
            player_list: gui.List
            player_list.remove_all()  # On supprime tout de la liste.
            content = args['content']

            content = content.split(', ')

            # On ajoute les noms de chaque joueur un par un.
            for player in content:
                player_btn = gui.Label(0, player[1:-1], (0, 0), (0, 0), Alignments.CENTER_LEFT, Colors.WHITE,
                                       "default", 40)
                player_list.add(player_btn)

    def main(self, args):
        """
        Gère l'affichage, évènements, etc.\n
        C'est la boucle principale du programme.
        """
        self.buttons = [
            gui.Button(0, "Construction", (20, window_height - 70), (190, 70), Colors.WHITE, Colors.RED_DARK,
                       "default", 40),
            gui.Button(5, "Mine", (220, window_height - 70), (100, 70), Colors.WHITE, Colors.RED_DARK, "default", 40)
        ]

        # Ajout d'un bouton pour chaque arme :
        position = 330
        i = 0
        while i < len(weapons):
            weapon = weapons[i]
            weapon_name = weapon[0]

            console.printLog(f"Adding button for weapon '{weapon_name}'.", [MessageTypes.INFO, MessageTypes.SECONDARY])
            self.buttons.append(
                gui.Button(1, weapon_name, (position * (i + 1), window_height - self.INVENTORY_HEIGHT),
                           (190, self.INVENTORY_HEIGHT), Colors.WHITE, Colors.RED_DARK, "default", 40)
            )
            i += 1

        # Ajout du texte (classe bouton mais désactivé) pour afficher les ressources...
        resources_button = gui.Button(2, "0", (20, 20), (200, 70), Colors.WHITE, Colors.DARK_GRAY, "default", 40)
        resources_button.disabled = True
        # ... pour afficher les ressources par seconde...
        rps_button = gui.Button(3, "10 r/s", (230, 20), (100, 70), Colors.WHITE, Colors.DARK_GRAY, "default", 40)
        rps_button.disabled = True
        # ... et pour afficher la santé du réacteur :
        reactor_button = gui.Button(4, "Santé du réacteur : 100%", (window_width - 20 - 500, 20), (500, 70),
                                    Colors.WHITE, Colors.DARK_GRAY, "default", 40)
        reactor_button.disabled = True

        try:
            self.player_number = int(args["content"])
            PyForts.settings.player_number = self.player_number  # On expose le numéro du joueur aux classes d'armes.
        except ValueError:
            console.printLog("Received incorrect message from server (player_number).", MessageTypes.ERROR)
            console.printLog("Game will now exit.", MessageTypes.ERROR)
            self.listen_thread.stop()
            exit(0)  # TODO:    Essayer de trouver une meilleure manière de résoudre le problème
            #                   (quitter la partie uniquement ou renvoyer un message au serveur)

        console.printLog("Playing as player number " + str(self.player_number + 1), MessageTypes.INFO)

        # Nouveaux évènements :
        self.event_handler.unbind_all()
        if self.player_number == 0:
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_CONSTRUCTION.value,
                                          self.update_player_base)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_CONSTRUCTION.value,
                                          self.update_opponent_base)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER_BASE_CONSTRUCTION.value,
                                          self.update_player_base)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_WEAPONS.value,
                                          self.update_player_weapons)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_WEAPONS.value,
                                          self.update_opponent_weapons)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_MINES.value,
                                          self.update_player_mines)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_MINES.value,
                                          self.update_opponent_mines)
        else:
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_CONSTRUCTION.value,
                                          self.update_opponent_base)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_CONSTRUCTION.value,
                                          self.update_player_base)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER_BASE_CONSTRUCTION.value,
                                          self.update_player_base)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_WEAPONS.value,
                                          self.update_opponent_weapons)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_WEAPONS.value,
                                          self.update_player_weapons)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_MINES.value,
                                          self.update_opponent_mines)
            self.event_handler.bind_event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_MINES.value,
                                          self.update_player_mines)

        self.event_handler.bind_event(pygame.USEREVENT + Messages.NEW_PROJECTILE.value,
                                      self.spawn_new_projectile)
        self.event_handler.bind_event(pygame.USEREVENT + Messages.DISCONNECT_PLAYERS.value,
                                      self.stop_game)

        clock = pygame.time.Clock()

        background = gui.Background(os.path.join('assets', 'level_1-background.jpg'), Alignments.CENTER,
                                    ScaleMode.COVER)

        # On fait apparaître les chouettes (réacteurs) :
        reactor_max_health = 300

        player1_reactor = gui.Reactor(
            (self.player1_grid_coordinates[0] + 200, self.player1_grid_coordinates[3] - self.grid_tile_size),
            (64, 64),
            reactor_max_health
        )
        player2_reactor = gui.Reactor(
            (self.player2_grid_coordinates[1] - 200, self.player1_grid_coordinates[3] - self.grid_tile_size),
            (64, 64),
            reactor_max_health
        )
        reactor_group = pygame.sprite.Group()
        reactor_group.add(player1_reactor)
        reactor_group.add(player2_reactor)

        # Bruit du réacteur :
        if settings['audio']['play_sound_effects']:
            reactor_sound = pygame.mixer.Sound(os.path.join('assets', 'sfx_chouette_2.ogg'))
            reactor_sound.play()

        tick = 0

        # Musique de la partie
        if settings['audio']['play_music']:
            # On joue une musique aléatoirement.
            music = random.choice([
                os.path.join('assets', 'pyforts_foret.ogg'),
                os.path.join('assets', 'pyforts_foret_nuit.ogg'),
                os.path.join('assets', 'pyforts_volcan.ogg'),
                os.path.join('assets', 'pyforts_espace.ogg')
            ])
            pygame.mixer.music.load(music)
            pygame.mixer.music.play(-1)

        # Boucle Principale
        while self.game_running:
            # Event Handling:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.listen_thread.stop()
                    self.server: net.ClientNetwork
                    self.server.send_message("", Messages.DISCONNECT_PLAYER)
                    self.server.disconnect()
                    self.game_running = False
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()

                    if self.buttons[0].pressed:  # L'utilisateur appuie sur le bouton pour construire :
                        # On gère le placement des points et des murs.
                        self.handle_construction()

                    player_weapons = self.player1_weapons \
                        if self.player_number == 0 else self.player2_weapons
                    player_weapons_group = self.player1_weapons_group \
                        if self.player_number == 0 else self.player2_weapons_group

                    for btn in self.buttons:
                        if btn.click(pos):
                            btn.switch_pressed()
                            if btn.id == 0:  # Bouton "Construction"
                                if not btn.pressed:
                                    self.points_group.empty()
                            if btn.id == 1:  # Tous les boutons d'armes ont l'id 1.
                                weapon = next((weapon for weapon in weapons if weapon[0] == btn.text), None)

                                # ça ne devrait jamais arriver, mais on ne sait jamais avec le contenu tiers.
                                if weapon is None:
                                    console.printLog(f"Weapon \"{btn.text}\" does not exist!", MessageTypes.ERROR)

                                if len(self.points_group.sprites()) == 1:
                                    weapon_class = weapon[1]
                                    weapon_projectile_class = weapon[2]

                                    if self.player_resources >= weapon[3]:
                                        self.player_resources -= weapon[3]
                                        # On crée l'arme à partir de la classe fournie
                                        weapon = weapon_class(player_weapons,
                                                              self.points_group.sprites()[0].rect.center[0],
                                                              self.points_group.sprites()[0].rect.center[1],
                                                              50, 50)
                                        player_weapons_group.append(weapon)
                                        self.points_group.empty()
                                        self.points_group.update()

                                        event_code = Messages.UPDATE_PLAYER1_BASE_WEAPONS.value \
                                            if self.player_number == 0 \
                                            else Messages.UPDATE_PLAYER2_BASE_WEAPONS.value
                                        event = pygame.event.Event(pygame.USEREVENT + event_code)
                                        pygame.event.post(event)
                                    else:
                                        console.printLog("Not enough resources to buy weapon.", [MessageTypes.INFO])
                                else:
                                    console.printLog("Not enough points to place weapon.", [MessageTypes.INFO])
                            if btn.id == 5:
                                # Mine
                                player_mines_plane = self.player1_mines_plane if self.player_number == 0 else \
                                    self.player2_mines_plane
                                if len(self.points_group.sprites()) == 1 and self.player_resources >= self.mine_cost\
                                        and len(player_mines_plane) < self.mine_max_number:
                                    self.player_resources -= self.mine_cost
                                    mine = gui.Mine(self.points_group.sprites()[0].rect.center, (80, 80))
                                    player_mines_plane.add(mine)

                                    mine_message = Messages.UPDATE_PLAYER1_BASE_MINES if self.player_number == 0 \
                                        else Messages.UPDATE_PLAYER2_BASE_MINES
                                    pygame.event.post(
                                        pygame.event.Event(pygame.USEREVENT + mine_message.value)
                                    )
                                    self.points_group.empty()
                                    self.points_group.update()

                    for weapon in player_weapons_group:
                        if weapon.selected and self.player_resources >= weapon.price:
                            projectile = weapon.shoot()
                            if projectile not in (None, True, False):
                                self.player_resources -= weapon.price

                                # Ajouter le projectile à la liste des projectiles
                                if self.player_number == 0:
                                    self.player1_projectiles_group.append(projectile)
                                else:
                                    self.player2_projectiles_group.append(projectile)
                                # On envoie le projectile au serveur.
                                message = (
                                    str(weapon.projectile_class),  # Classe du projectiles
                                    (projectile.image.rect.width, projectile.image.rect.height),  # Taille de l'image
                                    (projectile.x0, projectile.y0init),  # Position initiale du projectile
                                    round(projectile.angle, 2),  # Angle (arrondi à 10^-2)
                                    round(projectile.v0, 2),  # Norme du vecteur (arrondie à 10^-2) pour la force
                                    projectile.flip  # Affichage inversé de l'image
                                )
                                self.server.send_message(str(message), Messages.NEW_PROJECTILE)
                                pass
                        else:
                            if weapon.x - weapon.width // 2 < pos[0] < weapon.x + weapon.width // 2 and \
                                    weapon.y - weapon.height // 2 < pos[1] < weapon.y + weapon.height // 2:
                                weapon.click()
                else:
                    # On gère les autres évènements
                    self.event_handler.handle(event)

            # On vérifie que les réacteurs soient toujours là.
            player_reactor = player1_reactor if self.player_number == 0 else player2_reactor
            if player_reactor.hp <= 0:
                self.server.send_message(str(self.player_number), Messages.REACTOR_DEAD)

            clock.tick(gui.window_fps)
            tick += 1
            tick %= gui.window_fps

            # On ajoute des ressources au joueur :
            if tick == 0:  # Toutes les secondes
                if self.player_resources < self.player_max_resources:
                    self.player_resources += self.player_rps
                if self.player_resources > self.player_max_resources:
                    self.player_resources = self.player_max_resources

            player_mines_plane = self.player1_mines_plane if self.player_number == 0 else self.player2_mines_plane
            self.player_rps = self.player_default_rps + len(player_mines_plane.sprites()) * self.mine_rps_increase

            # AFFICHAGE

            # Il est possible que l'une de ces lignes génère une erreur TypeError ("Blit failed") si un message est
            # mal reçu. Mais ça ne devrait pas arriver plusieurs fois d'affilée.
            try:
                # Draw Window :
                window.blit(background.image, background.rect)

                if self.buttons[0].pressed:  # Si le bouton pour placer un mur est sélectionné
                    self.draw_grid(window)
                pygame.draw.rect(window, (50, 50, 50), (0, window_height - 50, window_width, self.INVENTORY_HEIGHT))

                # Affichage des réacteurs :
                reactor_group.draw(window)

                # Affichage des mines :
                self.player1_mines_plane.draw(window)
                self.player2_mines_plane.draw(window)

                # Affichage des bases :

                self.player1_construction_plane.draw(window)
                self.player2_construction_plane.draw(window)

                # Affichage des armes
                for group in (self.player1_weapons_group, self.player2_weapons_group):
                    for weapon in group:
                        # Si l'un des sprites de l'arme a été détruit, on supprime l'arme.
                        if len(weapon.image.groups()) == 0 or len(weapon.support_image.groups()) == 0:
                            group.remove(weapon)
                            del weapon.image
                            del weapon.support_image
                            del weapon
                        else:
                            weapon.update((self.player1_construction_plane, self.player2_construction_plane),
                                          self.player_resources)

                self.player1_weapons.update()
                self.player1_weapons.draw(window)

                self.player2_weapons.update()
                self.player2_weapons.draw(window)

                # Affichage des projectiles
                for projectile_group in (self.player1_projectiles_group, self.player2_projectiles_group):
                    for projectile in projectile_group:
                        if projectile.flip:
                            weapon_group = self.player1_weapons
                        else:
                            weapon_group = self.player2_weapons
                        projectile.update(
                            (self.player1_construction_plane, self.player2_construction_plane, weapon_group,
                             self.player1_mines_plane, self.player2_mines_plane),
                            reactor_group
                        )

                # Affichage de l'inventaire :
                pygame.draw.rect(window, (50, 50, 50), (0, window_height - 50, window_width, self.INVENTORY_HEIGHT))
            except TypeError:
                # Blit failed
                console.printLog("Could not display frame! Skipping frame.", MessageTypes.ERROR)
                pass

            # Affichage des boutons :
            for btn in self.buttons:
                if btn.id == 1:
                    if self.buttons[0].pressed:
                        btn.draw()

                        weapon = next((weapon for weapon in weapons if weapon[0] == btn.text), None)
                        if weapon is not None:
                            if len(self.points_group.sprites()) != 1 or weapon[3] > self.player_resources:
                                btn.disabled = True
                                btn.background_color = Colors.DARK_GRAY
                                btn.foreground_color = Colors.LIGHT_GRAY
                            else:
                                btn.disabled = False
                                btn.background_color = Colors.RED_DARK
                                btn.foreground_color = Colors.WHITE
                elif btn.id == 5:
                    if self.buttons[0].pressed:
                        btn.draw()

                        if len(self.points_group.sprites()) != 1 or self.mine_cost > self.player_resources \
                                or len(player_mines_plane.sprites()) >= self.mine_max_number:
                            btn.disabled = True
                            btn.background_color = Colors.DARK_GRAY
                            btn.foreground_color = Colors.LIGHT_GRAY
                        else:
                            btn.disabled = False
                            btn.background_color = Colors.RED_DARK
                            btn.foreground_color = Colors.WHITE
                else:
                    btn.draw()

            # On affiche le nombre de ressources :
            resources_button.text = str(self.player_resources)
            resources_button.draw()
            rps_button.text = str(self.player_rps) + " r/s"
            rps_button.draw()

            reactor_button.text = "Santé du réacteur : " + str(100*player_reactor.hp//reactor_max_health) + "%"
            reactor_button.draw()

            # Affichage des points de sélection :
            self.points_group.draw(window)

            pygame.display.update()
            # ------- FIN DE LA BOUCLE PRINCIPALE -------

        # Si on est ici, c'est que la partie s'est terminée.
        message = "Le serveur a quitté."
        background_color = Colors.RED_DARK
        if self.exit_code == 0:
            if self.player_number == 0:
                console.printLog("You won !", MessageTypes.INFO)
                message = "Vous avez gagné !"
                background_color = Colors.DARK_GREEN
            else:
                console.printLog("You lost !", MessageTypes.INFO)
                message = "Vous avez perdu."
        elif self.exit_code == 1:
            if self.player_number == 0:
                console.printLog("You lost !", MessageTypes.INFO)
                message = "Vous avez perdu."
            else:
                console.printLog("You won !", MessageTypes.INFO)
                message = "Vous avez gagné !"
                background_color = Colors.DARK_GREEN
        elif self.exit_code == 2:
            console.printLog("A player has disconnected.", MessageTypes.INFO)
            message = "Un joueur s'est déconnecté de la partie."

        background = gui.Background(os.path.join('assets', 'main_menu_background.png'), Alignments.CENTER,
                                    ScaleMode.COVER)
        logo = gui.Image(os.path.join('assets', 'pyforts_logo.png'), (gui.window_width // 2, 130),
                         (1681 // 2, 339 // 2))
        status_label = gui.Button(0, message, (10, window_height // 2 - 70 // 2),
                                  (gui.window_width - 20, 70),
                                  Colors.LIGHT_GRAY, background_color, "default", 40)
        status_label.disabled = True

        window.blit(background.image, background.rect)
        window.blit(logo.image, logo.rect)
        status_label.draw()
        waiting = True
        pygame.display.update()

        # On met la musique de la victoire / défaite
        if settings['audio']['play_music']:
            if self.exit_code == self.player_number:
                pygame.mixer.music.load(os.path.join('assets', 'pyforts_overture.ogg'))
            else:
                pygame.mixer.music.load(os.path.join('assets', 'pyforts_credits.ogg'))
            pygame.mixer.music.play(0)

        pygame.time.delay(1000)
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    exit()
                if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                    waiting = False
            pygame.display.update()

        # On met à nouveau la musique du menu principal
        if settings['audio']['play_music']:
            pygame.mixer.music.load(os.path.join('assets', 'pyforts_main_menu.ogg'))
            pygame.mixer.music.play(-1)

    def draw_grid(self, window):
        """
        Affiche la grille de construction à l'écran.

        :param window: Fenêtre pygame sur laquelle dessiner.
        """
        player_grid = self.player1_grid if self.player_number == 0 else self.player2_grid
        player_grid_coordinates = self.player1_grid_coordinates if self.player_number == 0 else \
            self.player2_grid_coordinates
        for x in range(0, player_grid["width"]):
            for y in range(0, player_grid["height"]):
                rect = pygame.Rect(player_grid_coordinates[0] + self.grid_tile_size * x,
                                   player_grid_coordinates[2] + self.grid_tile_size * y,
                                   self.grid_tile_size,
                                   self.grid_tile_size)
                pygame.draw.rect(window, Colors.DARKER_GRAY, rect, 1)

    def handle_construction(self):
        """
        Gère la construction (placement de points, de murs, etc.).
        """
        wants_to_place_a_point = False  # TODO: Renommer cette variable !
        pos = pygame.mouse.get_pos()

        # Si c'est le joueur 1 et que son curseur se trouve dans la grille :
        if not self.player_number and \
                (self.player1_grid_coordinates[0] <= pos[0] <= self.player1_grid_coordinates[1]) and \
                (self.player1_grid_coordinates[2] <= pos[1] <= self.player1_grid_coordinates[3]):
            # Alors on place un point :
            wants_to_place_a_point = True

            # Point Axe X
            pos_x = pos[0] - self.player1_grid["x"]  # Position du curseur par rapport à la grille.
            nearest_point_x = pos_x - (pos_x % self.grid_tile_size) + self.player1_grid["x"]
            if pos_x % self.grid_tile_size > self.grid_tile_size // 2:
                nearest_point_x += self.grid_tile_size

            # Point Axe Y
            pos_y = pos[1] + self.player1_grid["y"] + self.INVENTORY_HEIGHT
            nearest_point_y = pos_y - (pos_y % self.grid_tile_size) - self.player1_grid["y"] - \
                              self.INVENTORY_HEIGHT
            if pos_y % self.grid_tile_size > self.grid_tile_size // 2:
                nearest_point_y += self.grid_tile_size

        # Sinon, si c'est le deuxième joueur et que son curseur se trouve dans la grille :
        elif self.player_number and \
                (self.player2_grid_coordinates[0] <= pos[0] <= self.player2_grid_coordinates[1]) and \
                (self.player2_grid_coordinates[2] <= pos[1] <= self.player2_grid_coordinates[3]):
            # On fait la même chose pour trouver l'intersection la plus proche dans la grille :
            wants_to_place_a_point = True

            # Point Axe X
            pos_x = pos[0] - (window_width - self.player2_grid["x"] - self.player2_grid["width"] *
                              self.grid_tile_size)
            nearest_point_x = pos_x - (pos_x % self.grid_tile_size) + window_width - \
                              self.player2_grid["x"] - self.player2_grid["width"] * self.grid_tile_size
            if pos_x % self.grid_tile_size > self.grid_tile_size // 2:
                nearest_point_x += self.grid_tile_size

            # Point Axe Y
            pos_y = pos[1] + self.player2_grid["y"] + self.INVENTORY_HEIGHT
            nearest_point_y = pos_y - (pos_y % self.grid_tile_size) - self.player2_grid["y"] - \
                              self.INVENTORY_HEIGHT
            if pos_y % self.grid_tile_size > self.grid_tile_size // 2:
                nearest_point_y += self.grid_tile_size

        # Si le joueur souhaitait placer un point dans une grille
        if wants_to_place_a_point:
            new_point = gui.Point(pos_x=nearest_point_x, pos_y=nearest_point_y)
            # On vérifie le nombre de points déjà placés :
            if len(self.points_group.sprites()) > 0:
                    first_point = self.points_group.sprites()[-1]
                    distance = math.sqrt(
                        math.fabs((first_point.x - nearest_point_x) ** 2 +
                                  (first_point.y - nearest_point_y) ** 2)
                    )
                    if len(self.points_group.sprites()) > 1:
                        # S'il y a déjà deux points, on supprime le premier.
                        self.points_group.sprites()[0].kill()
                    if distance > math.sqrt(4000):
                        # On choisit 4000 pour avoir la distance maximum :
                        # sqrt(4000)=sqrt((20*3)**2+(20)**2)
                        # (20*3)**2 : hauteur max. (respectivement largeur max.)
                        # (20)**2 : largeur max. (respectivement hauteur max.)
                        self.points_group.sprites()[0].kill()
                        # Si le nouveau point est trop éloigné du premier, on supprime le premier.

            # Après avoir fait ces vérifications, on peut ajouter le nouveau point :
            self.points_group.add(new_point)

        # Si on a deux points sur la grille : on peut placer un mur !
        if len(self.points_group.sprites()) == 2:
            first_point = self.points_group.sprites()[0]
            second_point = self.points_group.sprites()[1]

            self.points_group.empty()
            self.points_group.update()
            if first_point.rect.center != second_point.rect.center and self.player_resources >= self.wall_price:
                # On vérifie qu'on n'ait pas cliqué sur le même point, sinon on place un mur :
                self.points_group.spritedict.get(0)
                wall = gui.Wall(x1=first_point.rect.x, y1=first_point.rect.y,
                                x2=second_point.rect.x, y2=second_point.rect.y)

                self.player_resources -= self.wall_price

                # On ajoute le mur au groupe de murs :
                event = None
                if self.player_number == 0:
                    self.player1_construction_plane.add(wall)
                    self.player1_construction_plane.update()
                    event = pygame.event.Event(pygame.USEREVENT + Messages.UPDATE_PLAYER1_BASE_CONSTRUCTION.value)
                elif self.player_number == 1:
                    self.player2_construction_plane.add(wall)
                    self.player2_construction_plane.update()
                    event = pygame.event.Event(pygame.USEREVENT + Messages.UPDATE_PLAYER2_BASE_CONSTRUCTION.value)

                # On poste un évènement pour dire que la base a été mise à jour :
                if event is not None:
                    pygame.event.post(event)
            else:
                console.printLog("Not enough resources to place a wall.", MessageTypes.INFO)

    def spawn_new_projectile(self, args):
        """
        Gère l'évènements NEW_PROJECTILE pour afficher un nouveau projectile ennemi à l'écran.

        :param args: Arguments passés par l'évènement. Contient les paramètres du projectile (classe, position, etc.)
        """
        # On récupère le groupe de projectiles du joueur :
        projectile_group = self.player1_projectiles_group if not self.player_number else self.player2_projectiles_group

        weapons_group = self.player1_weapons if self.player_number else self.player2_weapons

        # On ajoute le projectile au groupe de projectiles pour pouvoir le mettre à jour par la suite.
        prj = eval(args['content'])
        # Classe du projectile
        projectile_class = next((weapon for weapon in weapons if str(weapon[2]) == str(prj[0])), None)

        if projectile_class is not None:
            # On ajoute le projectile à la liste des projectiles.
            projectile_class = globals()['weapons'][globals()['weapons'].index(projectile_class)][2]
            new_projectile = projectile_class(weapons_group, prj[1], prj[2], prj[3], prj[4], prj[5])
            projectile_group.append(new_projectile)
        else:
            console.printLog("New projectile could not be loaded!", MessageTypes.ERROR)

    def update_player_base(self, args):
        """
        Envoie au serveur la nouvelle base du joueur.

        :param args: Arguments passés par l'évènement.
        """
        player_base = self.player1_construction_plane if self.player_number == 0 else self.player2_construction_plane
        message_code = Messages.UPDATE_PLAYER1_BASE_CONSTRUCTION if self.player_number == 0 else \
            Messages.UPDATE_PLAYER2_BASE_CONSTRUCTION
        base_to_send = []
        for wall in player_base.sprites():
            wall: gui.Wall  # Pour l'IDE.
            base_to_send.append((wall.x1, wall.y1, wall.x2, wall.y2))

        base_to_send = json.dumps(base_to_send)
        self.server.send_message(base_to_send, message_code)

    def update_player_weapons(self, args):
        """
        Envoie au serveur les armes du joueur.

        :param args: Arguments passés par l'évènement
        """
        player_weapons_group = self.player1_weapons_group if self.player_number == 0 else self.player2_weapons_group
        message_code = Messages.UPDATE_PLAYER1_BASE_WEAPONS if self.player_number == 0 else \
            Messages.UPDATE_PLAYER2_BASE_WEAPONS
        message_to_send = []
        for weapon in player_weapons_group:
            message_to_send.append((str(weapon.__class__), weapon.x, weapon.y, weapon.width, weapon.height))
        # message_to_send = json.dumps(str(message_to_send))
        self.server.send_message(str(message_to_send), message_code)

    def update_player_mines(self, args):
        """
        Envoie au serveur les nouvelles mines du joueur.

        :param args: Arguments passés par l'évènement.
        """
        player_mines = self.player1_mines_plane if self.player_number == 0 else self.player2_mines_plane
        message_code = Messages.UPDATE_PLAYER1_BASE_MINES \
            if self.player_number == 0 \
            else Messages.UPDATE_PLAYER2_BASE_MINES
        base_to_send = []
        for mine in player_mines.sprites():
            base_to_send.append((mine.pos, mine.size))
        self.server.send_message(str(base_to_send), message_code)

    def update_opponent_base(self, args):
        """
        Met à jour en local la base ennemie reçue du serveur.

        :param args: Arguments passés par l'évènement. Contient les coordonnées de chaque mur.
        """
        # Format du contenu du message reçu pour mettre à jour la base ennemie :
        # [[Mur1: x1, y1, x2, y2], [Mur2: x1, y1, x2, y2], ...]
        # Ne contient que des murs pour le moment.
        base = eval(args["content"])
        # La fonction eval permet d'interpréter une chaine de caractère comme du code Python.

        enemy_base = self.player2_construction_plane if self.player_number == 0 else self.player1_construction_plane
        enemy_base.empty()

        for wall in base:
            enemy_base.add(
                gui.Wall(wall[0], wall[1], wall[2], wall[3])
            )

        enemy_base.update()

    def update_opponent_weapons(self, args):
        """
        Met à jour en local les armes de l'ennemi.

        :param args: Arguments passés par l'évènement. Contient les coordonnées de chaque arme.
        """
        # Format du message reçu :
        # [(Nom de la classe, pos_x, pos_y, largeur, hauteur), (...), ...]
        message = eval(args['content'])
        opponent_weapons_group = self.player2_weapons_group if self.player_number == 0 else self.player1_weapons_group
        opponent_weapons = self.player2_weapons if self.player_number == 0 else self.player1_weapons

        opponent_weapons_group.clear()
        opponent_weapons.empty()

        for weapon in message:
            # On récupère la classe de l'arme
            weapon_class = next(
                (weapon_class[1] for weapon_class in weapons if str(weapon_class[1]) == weapon[0]),
                None
            )
            if weapon_class is not None:
                opponent_weapons_group.append(
                    weapon_class(opponent_weapons, weapon[1], weapon[2], weapon[3], weapon[4])
                )

        opponent_weapons.update()

    def update_opponent_mines(self, args):
        """
        Met à jour en local les mines de l'ennemi.

        :param args: Arguments passés par l'évènement. Contient les coordonnées de chaque arme.
        """
        message = eval(args['content'])
        opponent_mines_group = self.player1_mines_plane if self.player_number == 1 else self.player2_mines_plane

        opponent_mines_group.empty()

        for mine in message:
            new_mine = gui.Mine(mine[0], mine[1])
            opponent_mines_group.add(new_mine)

        opponent_mines_group.update()

    def stop_game(self, args):
        """
        Gère l'évènement DISCONNECT_PLAYERS qui indique la fin de la partie.

        :param args: Arguments passés par l'évènement. Contient le code de fermeture.
        """
        self.game_running = False

        self.event_handler.unbind_all()
        self.listen_thread.stop()
        self.server.disconnect()

        self.exit_code = int(args['content'])
