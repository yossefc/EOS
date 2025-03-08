# Gestion des états civils erronés

## Introduction

Le cahier des charges EOS prévoit des cas spécifiques où un dossier peut être considéré comme positif même si l'état civil trouvé ne correspond pas exactement à l'état civil fourni dans le dossier. Cette documentation explique comment gérer ces cas.

## Cas autorisés

D'après le cahier des charges, vous pouvez traiter un dossier avec un état civil légèrement différent dans les cas suivants :

1. **Un chiffre d'écart dans la date de naissance** : tous les autres éléments de l'état civil sont identiques. Par exemple : 12/06/1966 au lieu de 12/05/1966, ou 23/12/1984 au lieu de 03/12/1984.

2. **Deux chiffres d'écart dans la date de naissance avec confirmation par source non administrative** : tous les autres éléments de l'état civil sont identiques, et le résultat est confirmé par une source non administrative.

3. **Prénom différent mais correspond au 2ème ou 3ème prénom d'état civil** : tous les autres éléments de l'état civil sont identiques.

4. **Lieu de naissance différent avec confirmation par source non administrative** : tous les autres éléments sont identiques et le résultat est confirmé par une source non administrative.

5. **Date de naissance correspondant à celle du conjoint** : la date de naissance de l'intervenant recherché correspond à la date de naissance de son conjoint.

## Comment procéder

1. Lors du traitement d'une enquête, si vous identifiez l'un des cas ci-dessus, allez dans l'onglet "État civil" du formulaire.

2. Cochez "Oui (E)" pour le flag "État civil erroné".

3. Sélectionnez le type de divergence qui correspond à votre cas.

4. Renseignez l'état civil correct que vous avez trouvé.

5. N'oubliez pas d'ajouter des détails dans les commentaires pour justifier cette divergence.

6. Validez vos modifications.

## Important

- Le flag d'état civil erroné (E) **doit** être activé quand vous êtes dans l'un des cas listés ci-dessus.
- Si la divergence d'état civil ne correspond à aucun des cas autorisés, le traitement doit être "Intraitable" (I).
- Documentez toujours la source de vos informations, surtout quand une confirmation par source non administrative est requise.

## Conséquences pour l'export

Lors de l'export des données vers le format EOS, le système utilisera automatiquement l'état civil corrigé lorsque le flag "E" est activé. Ces informations seront transmises dans les zones d'état civil du fichier retour, conformément au cahier des charges.