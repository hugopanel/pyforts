###############
# MATH MODULE #
###############

import math


class Vec2d:
    def __init__(self, x=None, y=None, angle=None, magnitude=None):
        self._x = x
        self._y = y
        self._angle = angle
        self._magnitude = magnitude

        if x is not None and y is not None:
            self._update_properties()
        elif angle is not None and magnitude is not None:
            self._update_coordinates()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        # On change les coordonnées donc il faut recalculer l'angle et la norme du vecteur
        self._x = value
        self._update_properties()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        # On change les coordonnées donc il faut recalculer l'angle et la norme du vecteur
        self._y = value
        self._update_properties()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value % 360
        self._update_coordinates()

    @property
    def magnitude(self):
        return self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value
        self._update_coordinates()

    def dot(self, first_vector, second_vector):
        """Retourne le produit vectoriel entre ce vecteur et second_vector."""
        # Formule produit scalaire de deux vecteur à deux dimensions : <x1, y1>.<x2, y2> = x1*x2 + y1*y2
        return first_vector[0]*second_vector[0] + first_vector[1]*second_vector[1]

    def _update_coordinates(self):
        self._x = math.cos(self.angle)*self.magnitude
        self._y = math.sin(self.angle)*self.magnitude

    def _update_properties(self):
        self._magnitude = math.sqrt(math.fabs(self.x**2 + self.y**2))

        if self._magnitude != 0:  # Division par 0
            Simple_Vector = (1, 0)

            angle_cos = (Simple_Vector[0] * self.x + Simple_Vector[1] * self.y) \
                        / (Simple_Vector[0] * self.magnitude)
            self._angle = math.degrees(math.acos(angle_cos))
            if self.y > 0:
                self._angle = -self._angle