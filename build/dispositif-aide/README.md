# Dispositifs d'aides

Spécification du fichier d'échange relatif aux dispositifs d'aides.

## Composition

Ce schéma correspond au socle commun « Dispositifs d'aides », sans extension.

> 📖 **À propos** — Ce schéma fait partie d'un ensemble de schémas décrivant les dispositifs d'aides selon leur cible et pour différents usages. Pour le contexte et la finalité de l'ensemble, consultez la documentation principale.

## Champs (15)

| Champ | Libellé | Type | Obligatoire |
| --- | --- | --- | --- |
| `id` | Identifiant | string | Oui |
| `titre` | Titre | string | Oui |
| `promesse` | Promesse | string | Non |
| `description` | Description | string | Oui |
| `eligibilite` | Critères d’éligibilité | string | Oui |
| `types_aides` | Types d'aides | string | Oui |
| `porteurs` | Porteurs | string | Oui |
| `programmes_parents` | Programmes parents et régime d'aides | string | Non |
| `url_source` | URL Source | string | Non |
| `cibles` | Bénéficiaires | string | Oui |
| `eligibilite_geographique` | Couverture géographique de l’aide | string | Oui |
| `eligibilite_geographique_exclusions` | Couverture géographique de l’aide - Exclusions | string | Non |
| `date_ouverture` | Date d’ouverture | datetime | Non |
| `date_cloture` | Date de fin | datetime | Non |
| `date_mise_a_jour` | Date de dernière mise à jour | datetime | Oui |

## Ressources

- Schéma : [`schema.json`](schema.json)
- Exemple valide : [`exemple.csv`](exemple.csv)
