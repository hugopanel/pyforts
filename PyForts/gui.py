###################################
# GRAPHICAL USER INTERFACE MODULE #
###################################
import random

from PyForts.enums import ScaleMode, Alignments, Colors, TextInput_Type
from PyForts.settings import settings
from PyForts.math import Vec2d

import PyForts.events

import pygame
import os
import math

from typing import Tuple  # Pour les documentations de fonctions et classes.

window_width = settings["graphics"]["window_width"]
window_height = settings["graphics"]["window_height"]
window_fps = 60
window = pygame.display.set_mode((window_width, window_height))


class Label:
    def __init__(self, id, text, position, size, alignment, foreground_color, font_name, font_size):
        """
        Affiche un bloc de texte à l'écran.

        :param id: Identifiant du Label pour qu'il soit identifié si besoin.
        :param text: Texte à afficher dans le label.
        :param position: Position du label.
        :param size: Taille du bloc.
        :param foreground_color: Couleur du texte.
        :param font_name: Nom de la police d'écriture.
        :param font_size: Taille du texte.
        """
        self.id = id
        self.text = text
        self.position = position
        self.size = size
        self.alignment = alignment  # TODO: A implémenter, pour qu'on puisse centrer le texte.
        self.foreground_color = foreground_color
        self.font_name = font_name
        self.font_size = font_size

        self.rect = None

    def draw(self):
        """
        Affiche le label à l'écran.
        """
        font = pygame.font.SysFont(self.font_name, self.font_size, False, False)
        text = font.render(self.text, True, self.foreground_color)
        window.blit(text,
                    (
                        self.position[0],
                        self.position[1]
                    )
                    )  # center the text


class List:
    def __init__(self, id, elements, position, size, offset=100, empty_message=None, foreground_color=Colors.LIGHT_GRAY,
                 font_name="default", font_size=40):
        """
        Affiche une liste dynamique d'élements.

        :param id:
        :type id: int
        :param elements:
        :type elements: list
        :param position:
        :type position: Tuple[int, int]
        :param offset:
        :type offset: int
        :param empty_message:
        :type empty_message: str
        """
        self.id = id
        self.elements = elements
        self.position = position
        self.size = size
        self.offset = offset
        self.empty_message = empty_message
        self.foreground_color = foreground_color
        self.font_name = font_name
        self.font_size = font_size

    def add(self, element):
        self.elements.append(element)

    def remove(self, element):
        self.elements.remove(element)

    def remove_all(self):
        self.elements.clear()

    def index_of(self, element):
        return self.elements.index(element)

    def draw(self):
        if len(self.elements) == 0:
            font = pygame.font.SysFont(self.font_name, self.font_size, False, False)
            text = font.render(self.empty_message, True, self.foreground_color)
            window.blit(text,
                        (
                            self.position[0],
                            self.position[1]
                        )
                        )  # center the text
        else:
            for i in range(len(self.elements)):
                # On vérifie à chaque fois qu'il y ait bien le nombre d'éléments.
                # Avec les tâches asynchrones, on peut supprimer les éléments pendant la boucle.
                if i in range(len(self.elements)):
                    element = self.elements[i]
                    element.position = (self.position[0], self.position[1] + (i * self.offset))
                    element.draw()


class Button:
    def __init__(self, id, text, position, size, foreground_color, background_color, font_name,
                 font_size):
        """
        Affiche un bouton à l'écran.

        :param id: Identifiant du bouton pour qu'il soit identifié si besoin.
        :param text: Texte à afficher dans le bouton.
        :param position: Position du bouton.
        :param size: Taille du bouton
        :param foreground_color: Couleur du texte.
        :param background_color: Couleur du fond du bouton.
        :param font_name: Nom de la police d'écriture.
        :param font_size: Taille du texte.
        """
        self.id = id
        self.text = text
        self.position = position
        self.width = size[0]
        self.height = size[1]
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.font_name = font_name
        self.font_size = font_size

        self.disabled = False
        self.pressed = False

    def draw(self):
        """
        Affiche le bouton à l'écran.
        """
        mouse_pos = pygame.mouse.get_pos()
        background_color = self.background_color

        if (self.position[0] < mouse_pos[0] < self.position[0] + self.width) and \
                (self.position[1] < mouse_pos[1] < self.position[1] + self.height) and not self.disabled:
            background_color = (
            (background_color[0] + 40) % 255, (background_color[1] + 40) % 255, (background_color[2] + 40) % 255)
            if pygame.mouse.get_pressed(3)[0]:
                background_color = (
                (background_color[0] + 40) % 255, (background_color[1] + 40) % 255, (background_color[2] + 40) % 255)

        pygame.draw.rect(window, background_color, (self.position[0], self.position[1], self.width, self.height),
                         border_radius=10)
        font = pygame.font.SysFont(self.font_name, self.font_size, False, False)
        text = font.render(str(self.text), True, self.foreground_color)
        window.blit(text,
                    (
                        self.position[0] + round(self.width / 2) - round(text.get_width() / 2),
                        self.position[1] + round(self.height / 2) - round(text.get_height()) / 2
                    )
                    )  # center the text

    def click(self, position):
        """
        Clique sur le bouton si le curseur est au dessus.\n
        Pour cliquer dessus sans vérification, utiliser la fonction `switch_pressed`.

        :param position: Position du curseur.
        """
        # Check if the cursor is above the button.
        mouse_x = position[0]
        mouse_y = position[1]
        if self.position[0] <= mouse_x <= self.position[0] + self.width and \
               self.position[1] <= mouse_y <= self.position[1] + self.height and \
               not self.disabled:
            if settings['audio']['play_sound_effects']:
                click_sound = pygame.mixer.Sound(
                    random.choice([
                            os.path.join('assets', 'sfx_clic_1.ogg'),
                            os.path.join('assets', 'sfx_clic_2.ogg')
                        ])
                )
                click_sound.play()
            return True
        else:
            return False

    def switch_pressed(self):
        """
        Appuie sur le bouton, que le curseur soit au dessus ou non.
        """
        self.pressed = not self.pressed


class TextBox:
    def __init__(self, id, text, placeholder_text, text_input_type, size, position, foreground_color, background_color, font_name,
                 font_size, event_handler):
        self.id = id
        self.text = str(text)
        self.placeholder_text = str(placeholder_text)
        self.text_input_type = text_input_type
        self.size = size
        self.position = position
        self.foreground_color = foreground_color  # Check if foreground_color == None
        self.background_color = background_color
        self.font_name = font_name
        self.font_size = font_size

        self.selected = False
        self.disabled = False

        event_handler: PyForts.events.EventHandler

        event_handler.bind_event(pygame.KEYDOWN, self._handle_key_presses)

    def draw(self):
        """
        Affiche le champ d'entrée à l'écran.
        """
        mouse_pos = pygame.mouse.get_pos()
        background_color = self.background_color

        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        pos_x = self.position[0]
        pos_y = self.position[1]
        width = self.size[0]
        height = self.size[1]

        if not self.disabled:
            if (pos_x < mouse_x < pos_x + width) and (pos_y < mouse_y < pos_y + height) and not self.selected:
                background_color = (
                    (background_color[0] + 40) % 255,
                    (background_color[0] + 40) % 255,
                    (background_color[0] + 40) % 255
                )

        pygame.draw.rect(window, background_color, (pos_x, pos_y, width, height), border_radius=10)
        font = pygame.font.SysFont(self.font_name, self.font_size, False, False)

        text_to_print = None
        if self.text == "":
            text_to_print = self.placeholder_text
        else:
            text_to_print = self.text

        text = font.render(text_to_print, True, self.foreground_color)

        window.blit(text,
                    (
                        pos_x + round(width / 2) - round(text.get_width() / 2),
                        pos_y + round(height / 2) - round(text.get_height() / 2)
                    ))

        # On vérifie si le champ d'entrée est sélectionné. Si oui, on affiche un contour pour en informer l'utilisateur.
        if self.selected and not self.disabled:
            pygame.draw.rect(window, Colors.BLUE, (pos_x, pos_y, width, height), border_radius=10, width=3)

    def click(self, mouse_pos):
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        pos_x = self.position[0]
        pos_y = self.position[1]
        width = self.size[0]
        height = self.size[1]
        if pos_x <= mouse_x <= pos_x + width and pos_y <= mouse_y <= pos_y + height and not self.disabled:
            self.selected = True
            return True
        else:
            self.selected = False
            return False

    def switch_selected(self):
        self.selected = not self.selected

    def _handle_key_presses(self, args):
        if self.selected:
            if settings['audio']['play_sound_effects']:
                click_sound = pygame.mixer.Sound(
                    random.choice([
                            os.path.join('assets', 'sfx_clic_1.ogg'),
                            os.path.join('assets', 'sfx_clic_2.ogg')
                        ])
                )
                click_sound.play()
            if args['unicode'] == '\x08':  # Touche retour (effacer)
                self.text = self.text[:-1]
            elif args['unicode'] == '\x1b' or args['unicode'] == '\r':  # Touche Echap ou entrer
                self.selected = False
            else:
                if self.text_input_type == TextInput_Type.TEXT:
                    self.text += args['unicode']
                elif self.text_input_type == TextInput_Type.INTEGER:
                    if '0' <= args['unicode'] <= '9':
                        self.text += args['unicode']
                elif self.text_input_type == TextInput_Type.ADDRESS:
                    if '0' <= args['unicode'] <= '9' or args['unicode'] == '.':
                        # Si l'utilisateur entre un chiffre ou un point.
                        # Note : On ne peut pas mettre args['key'] == 59 pour le . car c'est le même numéro pour le ;
                        self.text += args["unicode"]
                elif self.text_input_type == TextInput_Type.FLOAT:
                    if '0' <= args['unicode'] <= '9' or args['unicode'] == ',':
                        self.text += args['unicode']


class Grid:
    def __init__(self, id, position, size):
        self.id = id
        self.position = position
        self.size = size

    def draw(self):
        pass


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location, scale_mode):
        """
        Image de fond d'écran.

        :param image_file: Chemin vers le fichier de l'image.
        :type image_file: str
        :param location: Position du centre de l'image sur l'écran.
        :type location: tuple[int, int] or Alignments
        :param scale_mode: Taille de l'image.
        :type scale_mode: ScaleMode
        """
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.rect = self.image.get_rect()

        self.location = location
        self.scale_mode = scale_mode

        self.update()

    def update(self):
        """
        Met à jour l'aspect de l'image (taille, position).
        """
        # Pour plus de lisibilité :
        scale_mode = self.scale_mode
        location = self.location

        window_width, window_height = pygame.display.get_window_size()

        # On met à jour la taille et la position de l'image, si la taille de la fenêtre change.
        if scale_mode == ScaleMode.STRETCH:
            self.image = pygame.transform.scale(self.image, (window_width, window_height))
        elif scale_mode == ScaleMode.COVER:
            """
            Ne marche pas totalement (formule incorrecte).
            Le but est de comparer le ratio de l'image avec celui de la fenêtre.
            """
            if window_width / window_height > self.image.get_width() / self.image.get_height():
                self.image = pygame.transform.scale(self.image,
                                                    (window_width,
                                                     self.image.get_height() * window_width // self.image.get_width()
                                                     )
                                                    )
            else:
                self.image = pygame.transform.scale(self.image,
                                                    (self.image.get_width() * window_height // self.image.get_height(),
                                                     window_height
                                                     )
                                                    )
        elif scale_mode == ScaleMode.TILE_HORIZONTAL_COVER:
            raise Exception("Pas encore implémenté !")

        self.rect = self.image.get_rect()

        if type(location) is Alignments:
            if location == Alignments.TOP_LEFT:
                self.rect.center = 0, 0
            elif location == Alignments.TOP_CENTER:
                self.rect.center = window_width // 2, 0
            elif location == Alignments.TOP_RIGHT:
                self.rect.center = window_width, 0
            elif location == Alignments.CENTER_LEFT:
                self.rect.center = 0, window_height // 2
            elif location == Alignments.CENTER:
                self.rect.center = window_width // 2, window_height // 2
            elif location == Alignments.CENTER_RIGHT:
                self.rect.center = window_width, window_height // 2
            elif location == Alignments.BOTTOM_LEFT:
                self.rect.center = 0, window_height
            elif location == Alignments.BOTTOM_CENTER:
                self.rect.center = window_width // 2, window_height
            elif location == Alignments.BOTTOM_RIGHT:
                self.rect.center = window_width, window_height
        else:
            self.rect.center = location


class Image(pygame.sprite.Sprite):
    def __init__(self, image_file, location, scale):
        """
        Image.

        :param image_file: Chemin vers le fichier de l'image.
        :type image_file: str
        :param location: Position du centre de l'image sur l'écran.
        :type location: tuple[int, int] or Alignments
        :param scale: Taille de l'image.
        :type scale: tuple[int, int]
        """
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.rect = self.image.get_rect()

        self.location = location
        self.scale = scale

        self.update()

    def update(self):
        """
        Met à jour l'aspect de l'image (taille, position).
        """
        # Pour plus de lisibilité :
        scale = self.scale
        location = self.location

        window_width, window_height = pygame.display.get_window_size()

        # On met à jour la taille et la position de l'image, si la taille de la fenêtre change.
        self.image = pygame.transform.scale(self.image, scale)

        self.rect = self.image.get_rect()

        if type(location) is Alignments:
            if location == Alignments.TOP_LEFT:
                self.rect.center = 0, 0
            elif location == Alignments.TOP_CENTER:
                self.rect.center = window_width // 2, 0
            elif location == Alignments.TOP_RIGHT:
                self.rect.center = window_width, 0
            elif location == Alignments.CENTER_LEFT:
                self.rect.center = 0, window_height // 2
            elif location == Alignments.CENTER:
                self.rect.center = window_width // 2, window_height // 2
            elif location == Alignments.CENTER_RIGHT:
                self.rect.center = window_width, window_height // 2
            elif location == Alignments.BOTTOM_LEFT:
                self.rect.center = 0, window_height
            elif location == Alignments.BOTTOM_CENTER:
                self.rect.center = window_width // 2, window_height
            elif location == Alignments.BOTTOM_RIGHT:
                self.rect.center = window_width, window_height
        else:
            self.rect.center = location


class Point(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        """
        Point, utilisé pour afficher une sélection.

        :param pos_x: Position axe X
        :param pos_y: Position axe Y
        """
        super().__init__()

        self.x, self.y = pos_x, pos_y

        self.image = pygame.image.load(os.path.join("assets", "point_selection.png"))
        self.rect = self.image.get_rect()

        self.rect.center = (self.x, self.y)

    def get_coordinates(self):
        """
        Retourne les coordonnées du point.

        :return: Tuple[int, int]
        """
        return self.x, self.y


class Wall(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2=0, y2=0, width=8, height=32):
        super().__init__()
        self.width, self.height = width, height
        # Correction des coordonnées (+8) puisqu'on récupère les bords du rectangle, pas le centre des points.
        # C'est temporaire, il faudrait faire diamètre/2 ou quelque chose du genre.
        # Il faudra changer de toute façon si on implémente une caméra et un zoom, puisque la taille changera.
        # C'est pas forcément ce qu'il y a de plus propre, mais c'est plus simple que de garder dans des variables les
        # points pour exposer leurs variables x et y.
        self.x1, self.y1 = x1 + 8, y1 + 8
        self.x2, self.y2 = x2 + 8, y2 + 8

        self.vec = Vec2d()
        if self.x2 != 0 and self.y2 != 0:
            # Pythagore pour calculer la hauteur du mur.
            self.height = math.sqrt(math.fabs((self.x2-self.x1)**2 + (self.y2-self.y1)**2))

            # Trouver l'inclinaison

            # Premier vecteur :
            first_vector = Vec2d(angle=0, magnitude=1)
            # Second vecteur :
            second_vector = Vec2d(x=(self.x2-self.x1), y=-(self.y2-self.y1))
            # Angle :
            # Produit vectoriel / produit des normes
            angle_cos = (first_vector.x * second_vector.x + first_vector.y * second_vector.y) \
                         / (first_vector.magnitude * second_vector.magnitude)
            self.angle = math.degrees(math.acos(angle_cos))
            if second_vector.y < 0:
                self.angle = -self.angle

            self.vec._angle = self.angle
            self.vec.magnitude = self.height

        # if current_plane == 0:
        #     self.original_image = pygame.image.load(PATH_TEX_BACKGROUND_WOODEN_WALL).convert_alpha()
        #     self.image = pygame.image.load(PATH_TEX_BACKGROUND_WOODEN_WALL).convert_alpha()
        # else:
        #     self.original_image = pygame.image.load(PATH_TEX_CONSTRUCTION_WOODEN_WALL).convert_alpha()
        #     self.image = pygame.image.load(PATH_TEX_CONSTRUCTION_WOODEN_WALL).convert_alpha()

        PATH_TEX_CONSTRUCTION_WOODEN_WALL = os.path.join("assets", "wooden_wall.png")
        self.original_image = pygame.image.load(PATH_TEX_CONSTRUCTION_WOODEN_WALL).convert_alpha()
        self.image = pygame.image.load(PATH_TEX_CONSTRUCTION_WOODEN_WALL).convert_alpha()

        self.rect = self.image.get_bounding_rect()
        self.rect.center = (self.x1 + (self.x2 - self.x1)/2, self.y1 + (self.y2 - self.y1)/2)

    def update(self):
        self.image = pygame.transform.scale(self.original_image, (self.width, int(self.vec.magnitude)))
        self.image = pygame.transform.rotate(self.image, -90 + self.vec.angle)  # -90° pour aligner la planche à 0°
        self.rect = self.image.get_bounding_rect()
        self.rect.center = (self.x1 + (self.x2 - self.x1)/2, self.y1 + (self.y2 - self.y1)/2)


class Reactor(pygame.sprite.Sprite):
    def __init__(self, position, size, max_hp):
        super().__init__()

        self.pos = position
        self.size = size
        self.hp = max_hp

        reactor_texture_path = os.path.join('assets', 'reactor.png')
        self.image = pygame.image.load(reactor_texture_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.center = position

    def deal_damage(self, damage_points):
        self.hp -= damage_points
        if self.hp <= 0:
            self.kill()


class Mine(pygame.sprite.Sprite):
    def __init__(self, position, size):
        super().__init__()

        self.pos = position
        self.size = size

        mine_texture = os.path.join('assets', 'mine.png')
        self.image = pygame.image.load(mine_texture).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.center = position
