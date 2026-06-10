# Dispositifs d'aides pour les professionnels

Extension du schéma dispositif-aide pour la cible 'professionnels'

## Composition

Ce schéma enrichit le socle commun « Dispositifs d'aides » avec les extensions suivantes :

- **Professionnels Extension** — Extension for business professionals (entreprises, indépendants) beneficiaries

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
| `taille_entreprise` | Taille d'entreprise acceptée | string | Non |
| `effectifs_minimum` | Nombre d'effectifs minimum | integer | Non |
| `effectifs_maximum` | Nombre d'effectifs maximum | integer | Non |
| `secteurs_activite` | Secteurs d'activité acceptés | string | Non |
| `chiffre_affaires_minimum` | Chiffre d'affaires minimum | number | Non |
| `chiffre_affaires_maximum` | Chiffre d'affaires maximum | number | Non |
| `statut_juridique` | Statuts juridiques acceptés | string | Non |
| `secteur_public_exclusion` | Exclusion secteur public | string | Non |
| `anciennete_minimum_mois` | Ancienneté minimum (mois) | integer | Non |

## Ressources

- Schéma : [`schema.json`](schema.json)
- Exemple valide : [`exemple.csv`](exemple.csv)
