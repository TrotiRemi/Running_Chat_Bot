# Texte Video LLM
## Schéma de la vidéo

 - Présentation du dataset (où nous avons trouvé les données)
 - Convertion des pdf et xlsx en csv
 - Convertion des données en un format adaptable pour l'entrainement : 

    1) Laver les données cassés
    2) Homogénisation des données
    3) Formatage des données en semaines
    4) Equilibrage du dataset pour éviter le suraprentisage des données sureprésenté

 - Lancement du notebook d'entrainement : 

    1) Importation du dataset
    2) Création du format d'apprentissage du LLM
    3) Separation des données en trois dataset (train, test et valid)
    4) Transformation des datasets pour l'apprentissage
    5) Importation du model GPT2
    6) Calcul des poigts iniciaux + de la loss initial
    7) Entrainement du model
    8) Validation du model et enregistrement

- Création d'un dashboard de discussion


## Texte de la vidéo
