# AI Use Log — Maxime Goulème
 
## Mon journal
  
| Date | Outil | Ce que j'ai demandé | Accepté / Modifié / Rejeté | Pourquoi (ce que j'ai vérifié, ce que j'ai trouvé) |
|---|---|---|---|---|
| 5 nov | Claude | Rédiger `requirements.md` au format SDD (EARS) à partir du brief | accepté | le prompte était claire et la réponse s'est basé sur le template ce qui a permit de faire un document clair |
| 5 nov | Claude | Écrire `train_resnet50.py` (fine-tuning ResNet-50 sur le dataset) | modifié | il m'a proposé un template, le prompte n'était pas assez claire sur la structure du projet |
| 14 nov | Claude | Lire le guidebook et construire le plan, le Trello et le notebook PR1 | modifié | m'a proposé aussi un template incomplet et pas assez clair mais a permis d'avoir une base sur laquelle travailler au lieu de partir de 0 |
| 14 nov | Claude | Mettre en place Kaggle et Colab pour télécharger le dataset | accepté | Testé dans Colab : le téléchargement marche sans compte Kaggle, 4 375 images, effectifs identiques au brief (Calculus 1 296, Hypodontia 1 251, etc.). |
| 14 nov | Claude | Notebook 01 (EDA, copies modifiées par dHash, images composites, split par groupes, manifest) et notebook 02 (entraînement), après mon observation que le dataset contient déjà des copies modifiées | modifié | Le seuil de copies par défaut (35) puis 48 laissait de la fuite : l'audit test/train montrait que 3 paires sur 4 les plus proches étaient la même photo (distance 49 à 52 bits). Seuil remonté à 60, distance minimale test→train de 61 bits. _(à compléter : ce que j'ai vu en regardant moi-même les nouvelles paires)_ |
| 14 nov | Claude | Relire le notebook de mon collègue (embeddings ResNet50) et le fusionner avec le mien (`01_EDA_et_manifest_v2.ipynb`) | accepté | Le rassemblement des différentes technique s'est avéré concluant, nous avons gardé les meilleurs techniques |
| 14 nov | Claude | Images composites : afficher les images juste au-dessus et en dessous du seuil, puis étiqueter à la main | modifié | Le score de couture ne sépare pas proprement : à 3 il coupe énormément de photos non collées, à 6 il y avait 5 images collées au-dessus du seuil et 4 images collées encore en dessous. Aucun seuil unique ne convient, donc j'ai étiqueté à la main. _(à compléter : nombre d'images étiquetées, ce que j'ai trouvé sur les images tirées au hasard)_ |
 
## Pistes de vérification concrètes (à faire vraiment, puis à écrire)
 
Ce sont les endroits où du code généré se trompe souvent sur ce type de projet. Vérifie-les, note ce que tu trouves.
 
- **Le split** : les images d'un même fichier peuvent-elles être dans train et test ? Compte les images par classe dans chaque split.
- **La métrique** : est-elle calculée sur le test, pas sur le train ni la validation ? Une seule fois à la fin ?
- **Le choix du meilleur modèle** : sur la validation, pas sur le test.
- **Les poids de classes** : calculés depuis le train uniquement.
- **Le chemin du dataset et les noms de classes** : correspondent-ils à ce qu'il y a vraiment sur le disque ?
- **Les doublons** : le contrôle détecte seulement les fichiers identiques octet par octet, pas les quasi-doublons.
- **Les versions de bibliothèques et noms d'API** : le code utilise-t-il vraiment des fonctions qui existent dans ta version ?
- **Ce que tu ne ferais pas confiance en production** : note au moins une partie de ton code dans ce cas (c'est valorisé par le guidebook).
