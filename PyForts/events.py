#############################
# EVENT HANDLER FOR PYFORTS #
#############################


class EventHandler:
    def __init__(self):
        """
        Gère les évènements PyGame et appelle les fonctions associées.\n
        Utilisez la classe `bind_event` pour associer une fonction à un évènement.
        """
        self._handlers_dict = {}

    def handle(self, event):
        """
        Appelle les fonctions associées à l'event passé en arguments.
        """
        if event.type in self._handlers_dict.keys():
            for func in self._handlers_dict[event.type]:
                event_dictionary = event.__dict__  # On envoie le dictionnaire de l'évènement à la fonction.
                event_dictionary["event_type"] = event.type  # On lui envoie aussi le type d'évènement "au cas où".
                func(event_dictionary)

    def bind_event(self, event_type, function):
        """
        Associe une fonction à un type d'évènements.\n
        Lorsqu'un évènement est déclenché, les fonctions associées sont exécutées.

        :param event_type: Type d'évènement PyGame.
        :param function: Fonction à associer à l'évènement.
        """
        if event_type not in self._handlers_dict.keys():
            self._handlers_dict[event_type] = []
        elif type(self._handlers_dict[event_type]) is not list:  # Cette ligne n'est peut être plus nécessaire.
            self._handlers_dict[event_type] = []
        if function not in self._handlers_dict[event_type]:
            self._handlers_dict[event_type].append(function)

    def unbind_event(self, event_type, function):
        """
        Dissocie une fonction d'un évènement.

        :param event_type: Type d'évènement
        :param function: Fonction à dissocier
        """
        if event_type in self._handlers_dict.keys():
            for i in range(self._handlers_dict[event_type].count(function)):
                self._handlers_dict[event_type].remove(function)

    def unbind_all(self):
        """
        Dossocie toutes les fontions de tous les évènements.
        """
        self._handlers_dict = {}
