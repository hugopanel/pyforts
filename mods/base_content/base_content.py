############################
# BASE CONTENT FOR PYFORTS #
############################

"""
Ce fichier stock le contenu de base du jeu.
Il est ainsi plus simple de modder le jeu ou d'y ajouter des DLCs.
"""

from PyForts.weapon import *


MOD_NAME = "PyForts Base Content"
MOD_DESCRIPTION = "Contenu de base du jeu Forts."
MOD_VERSION = "0.1"
MOD_AUTHOR = ["Evan ZANZUCCHI", "Hugo PANEL", "Mohamed ZAMMIT CHATTI", "Nathan MOREL", "Victor BOULET"]
MOD_COPYRIGHT = f"Copyright (c) 2020-2021, {', '.join(author for author in MOD_AUTHOR)}."


#---- Armes
class Mortar(Weapon):
    def __init__(self, sprite_group, x, y, width, height):
        self.force = {1: (100, 10), 2: (200, 13), 3: (250, 15), 4: (270, 20)}
        img_mortar = os.path.join("mods", "base_content", "assets", "mortar.png")
        img_mortar_support = os.path.join("mods", "base_content", "assets", "mortar_support.png")
        super().__init__(sprite_group, (x, y), (width, height), (30, 90), self.force, 1, img_mortar,
                         img_mortar_support, (0, 0), MortarProjectile, 20)


class MortarProjectile(Projectile):
    def __init__(self, sprite_group, image_size, position, angle, force, flip):
        fire_sounds = [
            os.path.join('assets', 'sfx_impact_1.ogg')
        ]
        explode_sounds = [
            os.path.join('assets', 'sfx_impact_2.ogg'),
            os.path.join('assets', 'sfx_impact_3.ogg'),
            os.path.join('assets', 'sfx_craquements.ogg')
        ]
        super().__init__(sprite_group, os.path.join("mods", "base_content", "assets", "bazooka_projectile.png"),
                         image_size, 0.1, position, angle, force, flip, fire_sounds, explode_sounds)


# On indique au jeu les classes qui correspondent à des armes.
weapons = [("Mortier", Mortar, MortarProjectile, 150, 20)]
