# Scripts de Contrôle Qualité Semi-Automatique - POEM 2022

## Objectif

Ces scripts sont une implémentation simple d'un processus de contrôle qualité semi-automatique.

Ce que font ces scripts :

+ Simplifie la validatation manuelle
+ applique des tests logiques sur les données avec des seuils prédétérminées pour attribuer des codes qualités

Ce que ne font pas ces scripts :

+ La recalibration 
+ L'interpolation de données

## Fichiers et Dossier

+ `manual_validator.py` : permet d'effectuer la "validation manuelle"
+ `qc_engine.py` : permet de générer un fichier avec les codes qualités en plus
+ `config.py` : permet une configuration simple du script `qc_engine.py`
+ `_build/` : contient les fichiers produit par le script `qc_engine.py`
+ `data/` : contient les données brutes et les fichiers produits par le script `manual_validator`
+ `readers/` : contient les librairies de lecture de fichiers brutes
+ `tools/` : contient les librairies aditionnels d'outils
+ `README.md` : ce fichier

## Préquis

Les scripts ont été écrits avec les versions de packages/librairies/logiciels suivantes. Les scripts n'ont pas été testé avec d'autres versions, cependant ils peuvent tout de même fonctionner.

+ Python 3.9.7 (dans un environnement conda/anaconda, de préférence)
+ Spyder 5 (disponible de base dans l'environnement conda/anaconda)
+ numpy 1.20.3
+ matplotlib 3.4.3
+ pandas 1.3.4

Il est également nécessaire d'afficher les graphiques matplotlib en mode fenêtré. Il faut configuer celà dans Spyder.

`Tools > Preferences > IPython console > Graphics > Graphics backend > Automatic`

## Usage / Processus

1. Validation manuelle
	
+ Lancer le script `manual_validator.py` dans l'interface spyder
+ selectionner sur quel paramètre effectuer la validation manuel dans la console (par exemple [0] puis [ENTER] pour effectuer la validation manuel de la temperature
+ enregister en cliquant sur [SAVE]
+ renouveler la manipulation pour chaquer paramètre


2. Contrôle Qualité Semi-Automatique

+ modifier la configuration dans `config.py` si necessaire
+ lancer le script `qc_engine.py` dans l'interface spyder

3. Recupérer les fichiers, ils devraient se trouver dans un sous dossier `_build/`

## Valeurs des codes qualités et leur signification
Code	Signification
+ 0	Contrôle qualité (QC) non effectué
+ 1	QC effectué : bonne donnée
+ 2	QC effectué : probablement bonne donnée
+ 3	QC effectué : probablement mauvaise donnée
+ 4	QC effectué : mauvaise donnée
+ 9	Donnée manquante

