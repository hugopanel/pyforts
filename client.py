##################
# PYFORTS CLIENT #
##################

"""
client.py

Copyright (c) 2021 :
Hugo PANEL, Nathan MOREL, Mohamed ZAMMIT CHATTI, Victor BOULET, Evan ZANZUCCHI
"""

from PyForts import *
from PyForts.settings import *
from PyForts.enums import *
from PyForts.events import EventHandler
import PyForts.gui as Gui
from PyForts.weapon import weapons

from moviepy.editor import VideoFileClip

import os
import importlib  # Pour importer les mods dynamiquement

import pygame

import game

print("Welcome to the PyForts client! Loaded game version", VERSION)


def main_menu():
    # Musique du menu principal
    if settings['audio']['play_music']:
        pygame.mixer.music.load(os.path.join('assets', 'pyforts_main_menu.ogg'))
        pygame.mixer.music.play(-1)

    Background = Gui.Background(os.path.join('assets', 'main_menu_background.png'), Alignments.CENTER, ScaleMode.COVER)
    Logo = Gui.Image(os.path.join('assets', 'pyforts_logo.png'), (Gui.window_width//2, 130), (1681//2, 339//2))

    buttons = [
        Gui.Button(0, "Rejoindre un serveur", (Gui.window_width//2-200, 250), (400, 70),
                   Colors.LIGHT_GRAY, Colors.DARK_GREEN, "default", 40),
        Gui.Button(1, "Armurerie", (Gui.window_width//2-200, 350), (400, 70),
                   Colors.DARK_GRAY, Colors.DARKER_GRAY, "default", 40),
        Gui.Button(2, "Paramètres", (Gui.window_width//2-200, 450), (400, 70),
                   Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40),
        Gui.Button(3, "Quitter", (Gui.window_width//2-200, 550), (400, 70),
                   Colors.WHITE, Colors.RED_DARK, "default", 40)
    ]

    buttons[1].disabled = True

    # MAIN MENU
    running = True
    while running:
        # Update window
        window.blit(Background.image, Background.rect)
        window.blit(Logo.image, Logo.rect)
        for button in buttons:
            button.draw()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Goodbye!")
                pygame.quit()
                exit(0)
            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    if button.click(pygame.mouse.get_pos()):
                        if button.id == 0:
                            # return connexion_screen
                            connexion_screen()
                        if button.id == 2:
                            # return settings_menu
                            settings_menu()
                        if button.id == 3:
                            running = False
                            # return False
                            pygame.quit()
                            exit(0)
        pygame.display.update()


def settings_menu():
    background = Gui.Background(os.path.join('assets', 'main_menu_background_blurred.png'),
                                Alignments.CENTER, ScaleMode.COVER)

    buttons = [
        Gui.Button(0, "< Retour", (10, 10), (Gui.window_width-20, 70),
                   Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40),
        Gui.Button(1, "Jouer la cinématique d'introduction", (10, 90), (Gui.window_width-20, 70),
                   Colors.LIGHT_GRAY, Colors.DARK_GREEN, "default", 40),
        Gui.Label(2, "Résolution :", (10, 180), (10, 10), Alignments.CENTER_LEFT, Colors.LIGHT_GRAY, "default", 40),
        Gui.Button(3, "1920x1080", (200, 170), (200, 70), Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40),
        Gui.Button(4, "1280x720", (410, 170), (200, 70), Colors.LIGHT_GRAY, Colors.DARK_GREEN, "default", 40)
    ]

    if settings["game"]["play_introduction"]:
        buttons[1].background_color = Colors.DARK_GREEN
    else:
        buttons[1].background_color = Colors.RED_DARK

    if settings["graphics"]["window_width"] == 1280:
        buttons[3].background_color = Colors.DARKER_GRAY
        buttons[4].background_color = Colors.DARK_GREEN
    elif settings["graphics"]["window_width"] == 1920:
        buttons[3].background_color = Colors.DARK_GREEN
        buttons[4].background_color = Colors.DARKER_GRAY

    running = True
    while running:
        # Update window
        window.blit(background.image, background.rect)
        for button in buttons:
            button.draw()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit(0)
            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    if type(button) == Gui.Button:
                        if button.click(pygame.mouse.get_pos()):
                            if button.id == 0:
                                running = False
                            elif button.id == 1:
                                settings["game"]["play_introduction"] = not settings["game"]["play_introduction"]
                                if settings["game"]["play_introduction"]:
                                    button.background_color = Colors.DARK_GREEN
                                else:
                                    button.background_color = Colors.RED_DARK
                                saveSettings()
                            elif button.id == 3:
                                settings["graphics"]["window_width"] = 1920
                                settings["graphics"]["window_height"] = 1080
                                buttons[3].background_color = Colors.DARK_GREEN
                                buttons[4].background_color = Colors.DARKER_GRAY
                                saveSettings()
                                Gui.window = pygame.display.set_mode((1920, 1080))
                                # Gui.window = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
                                Gui.window_width, Gui.window_height = 1920, 1080
                                return main_menu
                            elif button.id == 4:
                                settings["graphics"]["window_width"] = 1280
                                settings["graphics"]["window_height"] = 720
                                buttons[3].background_color = Colors.DARKER_GRAY
                                buttons[4].background_color = Colors.DARK_GREEN
                                saveSettings()
                                Gui.window = pygame.display.set_mode((1280, 720))
                                # Gui.window = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
                                Gui.window_width, Gui.window_height = 1280, 720
                                return main_menu
        pygame.display.update()

    return main_menu


def connexion_screen():
    background = Gui.Background(os.path.join('assets', "main_menu_background_blurred.png"),
                                Alignments.CENTER, ScaleMode.COVER)

    event_handler = EventHandler()

    elements = [
        Gui.Button(0, "< Retour", (10, 10), (Gui.window_width - 20, 70),
                   Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40),
        Gui.TextBox(1, settings["game"]["default_server_ip"], "Adresse IP du serveur", TextInput_Type.ADDRESS,
                    (Gui.window_width - 110, 70), (100, 110), Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40,
                    event_handler),
        Gui.TextBox(2, settings["game"]["default_server_port"], "Port du serveur", TextInput_Type.INTEGER,
                    (Gui.window_width - 110, 70), (100, 210), Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40,
                    event_handler),
        Gui.TextBox(3, USERNAME, "Username", TextInput_Type.TEXT,
                    (Gui.window_width - 110, 70), (100, 310), Colors.LIGHT_GRAY, Colors.DARKER_GRAY, "default", 40,
                    event_handler),
        Gui.Button(4, "Se connecter", (10, 410), (Gui.window_width - 20, 70),
                   Colors.LIGHT_GRAY, Colors.DARK_GREEN, "default", 40)

    ]

    running = True

    while running:
        # Update window
        window.blit(background.image, background.rect)
        Gui.Label(0, "IP :", (10, 130), (0, 0), Alignments.CENTER_LEFT, Colors.WHITE, "default", 40).draw()
        Gui.Label(0, "Port :", (10, 230), (0, 0), Alignments.CENTER_LEFT, Colors.WHITE, "default", 40).draw()
        Gui.Label(0, "Nom :", (10, 330), (0, 0), Alignments.CENTER_LEFT, Colors.WHITE, "default", 40).draw()
        for element in elements:
            element.draw()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit()
            event_handler.handle(event)
            if event.type == pygame.MOUSEBUTTONUP:
                for element in elements:
                    if type(element) is Gui.Button:
                        if element.click(pygame.mouse.get_pos()):
                            if element.id == 0:
                                running = False
                            if element.id == 4:
                                settings['game']['default_server_ip'] = elements[1].text
                                settings['game']['default_server_port'] = int(elements[2].text)
                                settings['profile']['username'] = elements[3].text
                                saveSettings()
                                lobby = game.Game(elements[1].text, elements[2].text, elements[3].text)
                                lobby.connect()
                    if type(element) is Gui.TextBox:
                        element.click(pygame.mouse.get_pos())

        pygame.display.update()
    return main_menu


# main_menu()
if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("PyForts " + str(VERSION) + " - Build b" + str(BUILD))
    # window = pygame.display.set_mode((window_width, window_height))
    window = Gui.window

    icon = pygame.image.load(os.path.join('assets', 'pyforts_icon.png'))
    pygame.display.set_icon(icon)

    # ---- Load mods
    # On regarde tous les mods dans settings.json :
    mods_to_import = []
    # mods_to_import Doc:
    # Chaque item est composé de :
    #   - Son nom (nom_du_mod)
    #   - Son chemin relatif (mods/nom_du_mod/nom_du_mod.py)
    #   - Son nom lors de l'importation (mods.nom_du_mod.nom_du_mod)
    for mod in settings["mods"]["mods"]:
        # On vérifie que le mod existe :
        if os.path.exists(os.path.join("mods", mod, mod + '.py')):
        # if mod[-3:] == ".py" and os.path.exists(os.path.join('mods', mod)):
            mods_to_import.append((mod, os.path.join('mods', mod, mod + '.py'), "mods." + mod + '.' + mod))
        else:
            console.printLog(f"Mod file \"{mod}\" was not found or is incompatible.", MessageTypes.ERROR)

    if len(mods_to_import) > 0:
        IS_MODDED = True

    for mod in mods_to_import:
        # Import mod:
        globals()["mod_" + mod[0]] = importlib.import_module(mod[2])
        # On ajoute chaque nouvelle arme dans la liste globale d'armes :
        for weapon in globals()["mod_" + mod[0]].weapons:
            weapons.append(weapon)

        mod_name = globals()["mod_" + mod[0]].MOD_NAME
        mod_version = globals()["mod_" + mod[0]].MOD_VERSION
        mod_copyright = globals()["mod_" + mod[0]].MOD_COPYRIGHT
        console.printLog(f"Successfully imported mod \"{mod_name}\" version {mod_version}", MessageTypes.INFO)
        console.printLog(f"Mod copyright: {mod_copyright}", MessageTypes.INFO)

        # On ajoute à la liste globale de mods le nom (du fichier, sans extension) de chaque mod.
        mods_list.append(mod[0])
        # TODO: Envoyer la liste des mods et la variable IS_MODDED au serveur lors de la connexion.

    # Cinématique d'introduction
    if settings["game"]["play_introduction"]:
        intro_movie = VideoFileClip(os.path.join('assets', 'Overture.mp4'))
        intro_movie.fps = 25
        intro_movie = intro_movie.resize(width=Gui.window_width, height=Gui.window_height)
        intro_movie.preview()

    main_menu()
