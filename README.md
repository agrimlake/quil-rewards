# Quilibrium Rewards Tool

Ce script Python permet de rechercher et d'afficher les informations de récompense pour des pairs spécifiques dans le réseau Quilibrium. Vous pouvez retrouvez ces informations directement sur le site de https://quilibrium.com/rewards . Il permet d'extraire les données des récompenses à partir du site web de Quilibrium et fournit une ventilation détaillée des récompenses pour chaque pair.
Il fournit également quelques estimations/suppositions quand à la présence ou non des peers sur le réseau Quilibrium (Information non fiable)

## Fonctionnalités

- Recherche les informations de récompense pour des pairs spécifiques en utilisant leur PeerId
- Affiche les détails des récompenses, y compris le montant de la récompense, la présence mensuelle, les critères, le solde existant, etc.
- Calcule et affiche les statistiques globales sur la distribution des récompenses pour tous les nœuds. (Attention valeur non fiable)
- Prend en charge la recherche de pairs à partir d'un fichier ou en passant directement les PeerId en argument de ligne de commande

## Prérequis

- Python 3.8 ou version supérieure
- Module `requests` (installé via `pip` ou `pip3` ci-dessous)

## Installation

1. Clonez ce dépôt ou téléchargez le script `quil-rewards.py`.

2. Installez les dépendances requises en exécutant la commande suivante :

  ```bash
pip install -r requirements.txt
  ```

ou

  ```bash
pip3 install -r requirements.txt
  ```

## Utilisation

  Modifiez le fichier peers.lst et ajoutez les PeerId des pairs que vous souhaitez rechercher, un par ligne.
  Exécutez le script en utilisant l'une des méthodes suivantes :

  Sans arguments (utilisera peers.lst par défaut) :

  ```bash 
  python quil-rewards.py
  ```

  En spécifiant les PeerId directement en argument :
  ```bash 
  python quil-rewards.py --peer_ids <peer_id_1> <peer_id_2> ...
  ```

  En spécifiant un fichier contenant les PeerId :
  ```bash
  python quil-rewards.py --file <chemin_vers_le_fichier>
  ```



Le script affichera les informations de récompense pour chaque pair trouvé, ainsi que les statistiques globales sur la distribution des récompenses.

Exemple d'utilisation
```bash
python quil-rewards.py --peer_ids QmaBCDEF1234567890 QmXYZ0987654321
```

Cela recherchera les informations de récompense pour les pairs avec les PeerId `QmaBCDEF1234567890` et `QmXYZ0987654321` et affichera les détails correspondants.

## Contribuer
Les contributions sont les bienvenues ! Si vous trouvez des bogues, avez des suggestions d'amélioration ou souhaitez ajouter de nouvelles fonctionnalités, n'hésitez pas à ouvrir une issue ou à soumettre une pull request.
