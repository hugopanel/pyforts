# Convention de code

Afin que le développement du projet se déroule de la meilleure manière possible, il faurda suivre certaines règles et coventions, notamment lorsque vous nommez vos variables et fonctions.


# Nomenclature

Voici un résumé les règles à suivre lorsque vous nommez de nouvelles variables ou fonctions.
Pour plus de détails, visitez [PEP 8 - Naming Conventions](https://www.python.org/dev/peps/pep-0008/#naming-conventions).

- Les classes doivent être nommées en CamelCase (ex: MaClasse).
- Les fonctions et variables doivent être en minuscules séparées par des underscores (ex: particle_size, show_widget()).
- Les arguments de fonctions doivent être en minuscules séparées par des underscores (ex: fonction(size, particle_density).
- Les variables et fonctions privées doivent être précédées d'un underscore (ex: _density).
- Les constantes doivent être en MAJUSCULES (ex: LIB_VERSION). 


# Code propre

Lors de la rédaction de code, suivez ces différentes conventions :

## Indentation

Python 3 est plus strict que Python 2 par rapport à l'intentation. Si le code utilise à la fois des tabulations et des espaces, des erreurs apparaîtront, et il faut décider entre les deux. Nous allons donc dans ce projet suivre les conventions indiquées dans PEP 8 par Python et utiliser **4 espaces** pour l'indentation. C'est le choix par défaut sur PyCharm (utiliser la touche tabulation insert 4 espaces).

## Lignes vides et espaces

Les classes et fonctions doivent être précédées et suivies de deux lignes vides. Les fonctions inscrites dans une classe doivent être précédées et suivies d'une seule ligne vide.
Les commentaires sont ignorés.
```python
# Exemple
def fonction(argument):
    return argument


def fonction2(argument):
    return argument


# Cette ligne est collée mais ça reste correct.
def fonction3(argument):
    return argument


class Classe:
    def classeFonction():
        # La première fonction peut être collée à la classe.
        pass

    def classeFonction2():
        # Les fonctions sont en suite séparés par une seule ligne dans les classes.
        pass
```
## Docstrings 

Les fonctions et classes doivent toutes posséder une chaîne de caractères d'explications (docstrings). Pour savoir ce à quoi ça ressemble, et comment en écrire, consultez [PEP 257](https://www.python.org/dev/peps/pep-0257/).

## Exceptions

Dès que possible, préciser l'exception attendue dans un try except:
```python
try:
    with file.open(...) as settings_file:
        ...
except:
    ...

# Devrait être :
try:
    with file.open(...) as settings_file:
        ...
except IOFileNotFoundError:
    ...
```

# Ressources

Si vous souhaitez en savoir plus sur les conventions d'écriture de code, voici des documents qui ont inspiré celui-ci :
- [Python Code Convention with Python](https://developer.rhino3d.com/guides/rhinopython/python-code-conventions/#:~:text=Python%20Code%20Conventions%201%20Overview.%20Coding%20conventions%20are,by%20the%20interpreter%20during%20compile.%20Plus%20d%27articles...%20) Très résumé
- [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) Très détaillé
