# AI Use Log — Maxime Goulème
 
## Mon journal
  
| Date | Outil | Ce que j'ai demandé | Accepté / Modifié / Rejeté | Pourquoi (ce que j'ai vérifié, ce que j'ai trouvé) |
|---|---|---|---|---|
| 5 nov | Claude | Rédiger `requirements.md` au format SDD (EARS) à partir du brief | accepté | le prompte était claire et la réponse s'est basé sur le template ce qui a permit de faire un document clair |
| 5 nov | Claude | Écrire `train_resnet50.py` (fine-tuning ResNet-50 sur le dataset) | modifié | il m'a proposé un template, le prompte n'était pas assez claire sur la structure du projet |
| 14 nov | Claude | Lire le guidebook et construire le plan, le Trello et le notebook PR1 | modifié | m'a proposé aussi un template incomplet et pas assez clair mais a permis d'avoir une base sur laquelle travailler au lieu de partir de 0 |
 
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
