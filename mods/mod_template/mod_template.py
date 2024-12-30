############
# MOD NAME #
############

"""
Bienvenue sur le modèle de mods.
Les mods vous permettent d'ajouter ou de modifier du contenu au jeu.
Ce modèle vous permettra de développer votre propre mod et de le rendre compatible avec PyForts.

/!\ Certains serveurs peuvent refuser la connexion des clients moddés.
"""

# Imports:
import PyForts.console as console
from PyForts.enums import MessageTypes
from PyForts.weapon import Weapon, Projectile
import os


# Information about your mod:
MOD_NAME = "Your mod name."
MOD_DESCRIPTION = "A short description of what your mod does."
MOD_VERSION = "1.0"
MOD_AUTHOR = ["Your name"]
MOD_COPYRIGHT = f"Copyright (c) year, {', '.join(author for author in MOD_AUTHOR)}."

# Custom code
console.printLog("Loaded my custom mod.", [MessageTypes.INFO, MessageTypes.SECONDARY])


#---- Weapons:
class MyNewWeapon(Weapon):
    def __init__(self, sprite_group, x, y, width, height):
        # Weapon's force levels.
        # --> {level: (force, reload time), ...}
        self.force = {1: (100, 10), 2: (200, 13)}
        # Import your own images
        img_mortar = os.path.join("mods", "", "assets", "my_weapon.png")
        img_mortar_support = os.path.join("mods", "", "assets", "my_weapon_base.png")
        # Call super init function
        super().__init__(sprite_group, (x, y), (width, height), (30, 100), self.force, 1, img_mortar,
                         img_mortar_support, (0, 0), MyNewWeaponsProjectile)


class MyNewWeaponsProjectile(Projectile):
    def __init__(self, sprite_group, image_size, position, angle, force, flip):
        fire_sounds = [
            os.path.join('assets', 'sfx_impact_1.ogg')
        ]
        explode_sounds = [
            os.path.join('assets', 'sfx_impact_2.ogg')
        ]
        super().__init__(sprite_group, os.path.join("mods", "", "assets", "my_projectile.png"),
                         image_size, 0.2, position, angle, force, flip, fire_sounds, explode_sounds)


# Declare which classes are weapons.
weapons = [("My New Weapon's Name", MyNewWeapon, MyNewWeaponsProjectile)]
