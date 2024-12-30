#################################
# BASE CLASSES FOR EVERY WEAPON #
#################################


import pygame
import os
import math
import pygame.gfxdraw
import random

from PyForts.enums import Messages
from PyForts.math import *

from PyForts.gui import window, window_width, window_height, window_fps
from PyForts.settings import settings


# Liste de toutes les armes du jeu. Est complétée au lancement du jeu grâce aux mods.
weapons = []


class WeaponSprite(pygame.sprite.Sprite):
    def __init__(self, image_path, size):
        super().__init__()

        self.width = 40
        self.height = 40

        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (size[0], size[1]))
        self.image = self.original_image

        self.rect = self.image.get_rect()

        self.current_angle = 0

    def rotate(self, angle):
        self.image = pygame.transform.rotozoom(self.original_image, angle, 1).convert_alpha()
        self.current_angle = angle
        self.rect = self.image.get_rect()


class Weapon:
    def __init__(self, sprite_group, position, size, range, force_levels, level, image, support_image, support_offset,
                 projectile_class, shoot_cost):
        super().__init__()
        self.angle = 0
        self.range = range
        self.force_levels = force_levels
        self.level = level
        self.range_rect = pygame.rect

        self.x = position[0]
        self.y = position[1]

        self.width = size[0]
        self.height = size[1]

        self.image = WeaponSprite(image, size)

        self.support_image = WeaponSprite(support_image, size)

        self.image.rect.center = position
        self.support_image.rect.center = (position[0] + support_offset[0], position[1] + support_offset[1])

        self.sprite_group = sprite_group
        self.sprite_group.add(self.image)
        self.sprite_group.add(self.support_image)

        self.projectile_class = projectile_class
        self.projectiles = []

        self.price = shoot_cost

        self.timer = 0
        self.selected = False
        self.last_position = (0, 0)

        # Change range depending on the player number:
        if self.x > window_width//2:
            self.range = (
                math.degrees(math.acos(-math.cos(math.radians(self.range[1])))),
                math.degrees(math.acos(-math.cos(math.radians(self.range[0]))))
            )

        # On met l'arme dans un angle possible par défaut.
        self.angle = self.range[0]
        self.image.rotate(self.angle)
        self.image.rect.center = self.x, self.y

    def update(self, walls_groups, player_resources):
        mouse_pos = pygame.mouse.get_pos()

        # Update the weapon itself
        if self.selected:
            # Faire tourner l'arme pour suivre le curseur
            x = mouse_pos[0] - self.x
            y = mouse_pos[1] - self.y
            curs_vec = Vec2d(x=x, y=y)

            if curs_vec.angle is not None:
                self.angle = math.floor(curs_vec.angle)
            else:
                self.angle = 0

            if self.angle < self.range[0]:
                self.angle = self.range[0]
            elif self.angle > self.range[1]:
                self.angle = self.range[1]

            self.image.rotate(self.angle)
            self.image.rect.center = self.x, self.y

            force_min = self.force_levels[self.level][0] - self.force_levels[self.level][0] / 2
            force_max = self.force_levels[self.level][0]

            # Affichage des limites du tir
            rectangle_min = (self.x - force_min, self.y - force_min, force_min * 2, force_min * 2)
            rectangle_max = (self.x - force_max, self.y - force_max, force_max * 2, force_max * 2)

            # Affichage du temps de rechargement.
            # TODO: Changer le sens pour le joueur 2.
            if self.timer > 0:
                pygame.draw.arc(window, (127, 0, 0,),
                                rectangle_max,
                                math.radians(self.range[0]),    # Angle inférieur
                                math.radians(                   # Angle supérieur
                                    (self.timer/window_fps*(self.range[1]-self.range[0]))
                                    / self.force_levels[self.level][1]+self.range[0]),
                                int(force_max-force_min))

            # Limite inférieure
            pygame.draw.arc(window, (0, 0, 0), rectangle_min,
                            math.radians(self.range[0]), math.radians(self.range[1]), 1)
            # Limite supérieure
            pygame.draw.arc(window, (0, 0, 0), rectangle_max,
                            math.radians(self.range[0]), math.radians(self.range[1]), 1)

            pygame.draw.circle(window, (0, 0, 127), self.last_position, 2, 0)

            # Affichage du vecteur
            if curs_vec.angle is not None and curs_vec.magnitude is not None:
                if self.range[0] <= curs_vec.angle <= self.range[1] and force_min <= curs_vec.magnitude <= force_max:
                    color = (0, 255, 0)
                    if self.timer != 0 or player_resources < self.price:
                        color = (255, 0, 0)
                    pygame.draw.line(window, color, (self.x, self.y), mouse_pos)

        if self.timer > 0:
            self.timer -= 1

    def shoot(self):
        mouse_pos = pygame.mouse.get_pos()

        x = mouse_pos[0] - self.x
        y = mouse_pos[1] - self.y
        v0 = Vec2d(x=x, y=y)

        force_min = self.force_levels[self.level][0] - self.force_levels[self.level][0] / 2
        force_max = self.force_levels[self.level][0]

        # Vérification de la position du curseur
        if self.range[0] <= v0.angle <= self.range[1] and force_min <= v0.magnitude <= force_max:
            # Tir
            if self.timer == 0:
                self.last_position = mouse_pos

                projectile = self.projectile_class(self.sprite_group, (30, 30), (self.x, self.y), self.angle,
                                                   (v0.magnitude//force_min +
                                                    self.force_levels[self.level][0]//force_max),
                                                   True if self.x > window_width//2 else False)

                self.timer = self.force_levels[self.level][1]*window_fps  # Attendre avant de pouvoir tirer à nouveau.

                return projectile
        else:
            # On déselectionne l'arme
            self.selected = False
            return False

    def upgrade(self):
        # Augmentation de la force de l'arme
        self.level += 1

    def click(self):
        self.selected = not self.selected


class Projectile:
    def __init__(self, sprite_group, image, image_size, time_add, position, angle, force, flip, fire_sounds,
                 explode_sounds):
        self.t = 0
        self.t_add = time_add

        self.fire_sounds = fire_sounds
        self.explode_sounds = explode_sounds

        self.image = WeaponSprite(image, image_size)
        sprite_group.add(self.image)

        self.shot = False

        self.x0 = self.x = self.y0 = self.y = self.angle = self.v0 = self.vx = self.vy = self.sx = self.sy = 0
        self.g = 9.80665
        self.top = 0

        self.flip = flip
        self.x0 = self.x = position[0]  # Déjà dans le bon sens
        self.y = position[1]  # Exprimé dans le sens de PyGame (du haut vers le bas)
        self.y0init = position[1]  # Valeur initiale de y0 (pour obtenir la position du projectile autre part)
        self.y0 = window_height - position[1]  # Exprimé du bas vers le haut
        self.angle = angle
        self.v0 = force

        self.vx = math.degrees(math.cos(math.radians(angle))) * force
        self.vy = math.degrees(math.sin(math.radians(angle))) * force

        self.sx = self.vx

        self.destroyed = False

        # On joue le son du tir
        if settings['audio']['play_sound_effects']:
            fire_sound = random.choice(self.fire_sounds)
            fire_sound = pygame.mixer.Sound(fire_sound)
            fire_sound.play()

    def update(self, walls_groups, reactors_group):
        if self.y < window_height + 10:
            self.x = self.vx * self.t + self.x0

            self.y = self.y0 + -1/2 * (self.g / ((math.degrees(math.cos(math.radians(self.angle))) * self.v0) ** 2)) * \
                ((self.x - self.x0) ** 2) + ((math.degrees(math.sin(math.radians(self.angle))) * self.v0) /
                (math.degrees(math.cos(math.radians(self.angle))) * self.v0)) * (self.x - self.x0)

            delta_x = (self.x-self.x0)*1.7  # On fait *1.7 pour corriger l'angle du projectile (visuel uniquement)

            derivee = 2 * (-self.g / (2 * math.degrees(math.cos(math.radians(self.angle))) * self.v0) ** 2) * delta_x \
                      + ((math.degrees(math.sin(math.radians(self.angle))) * self.v0) /
                         (math.degrees(math.cos(math.radians(self.angle))) * self.v0))

            tangente = derivee * ((delta_x + 1) - delta_x) + self.y

            Vector = Vec2d(x=1, y=tangente - self.y)

            self.t += self.t_add
            self.image.rotate(-Vector.angle) if not self.flip else self.image.rotate(-Vector.angle+180)
            self.y = window_height - self.y
            self.image.rect = self.image.image.get_rect()
            self.image.rect.center = self.x, self.y

            # Affichage de la boîte de collisions.
            # pygame.draw.rect(window, (0, 0, 0), self.image.rect, 1)

            # Vérification des collisions
            for walls_group in walls_groups:
                bCollides = pygame.sprite.spritecollide(self.image, walls_group, dokill=False)
                if bCollides:
                    for element in bCollides:
                        element.kill()
                        event = pygame.event.Event(pygame.USEREVENT + Messages.UPDATE_PLAYER_BASE_CONSTRUCTION.value)
                        pygame.event.post(event)
                    self.image.kill()
                    self.destroyed = True
                    # On joue le son de l'explosion
                    if settings['audio']['play_sound_effects']:
                        explode_sound = random.choice(self.explode_sounds)
                        explode_sound = pygame.mixer.Sound(explode_sound)
                        explode_sound.play()

            bCollides = pygame.sprite.spritecollide(self.image, reactors_group, dokill=False)
            if bCollides:
                for reactor in bCollides:
                    reactor.deal_damage(self.v0)
                    self.destroyed = True
                    # On joue le son de l'explosion
                    if settings['audio']['play_sound_effects']:
                        explode_sound = random.choice(self.explode_sounds)
                        explode_sound = pygame.mixer.Sound(explode_sound)
                        explode_sound.play()
        else:
            self.destroyed = True
