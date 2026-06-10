# Dispositifs d'aides (activation)

Extension du schéma dispositif-aide avec les extensions d'usage : activation

## Composition

Ce schéma enrichit le socle commun « Dispositifs d'aides » avec les extensions suivantes :

- **ExteExtension d'usage - activation** — Extension créée pour une démonstration, champs non validés - Extension pour définir des aides plus facilement activables

> 📖 **À propos** — Ce schéma fait partie d'un ensemble de schémas décrivant les dispositifs d'aides selon leur cible et pour différents usages. Pour le contexte et la finalité de l'ensemble, consultez la documentation principale.

## Champs (24)

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
| `eligibilite_geographique_exclusions` | Couverture géographique de l’aide - exclusions | string | Non |
| `date_ouverture` | Date d’ouverture | datetime | Non |
| `date_cloture` | Date de fin | datetime | Non |
| `date_mise_a_jour` | Date de dernière mise à jour | datetime | Oui |
| `objectif1` | Objectif 1 | string | Non |
| `lien1` | Lien 1 | string | Non |
| `texte_lien1` | Texte du lien 1 | string | Non |
| `objectif2` | Objectif 2 | string | Non |
| `lien2` | Lien 2 | string | Non |
| `texte_lien2` | Texte du lien 2 | string | Non |
| `objectif3` | Objectif 3 | string | Non |
| `lien3` | Lien 3 | string | Non |
| `texte_lien3` | Texte du lien 3 | string | Non |

## Ressources

- Schéma : [`schema.json`](schema.json)
- Exemple valide : [`exemple.csv`](exemple.csv)
