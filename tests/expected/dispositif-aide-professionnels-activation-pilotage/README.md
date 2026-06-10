# Dispositifs d'aides pour les professionnels (activation, pilotage)

Extension du schéma dispositif-aide pour la cible 'professionnels' avec les extensions d'usage : activation, pilotage

## Composition

Ce schéma enrichit le socle commun « Dispositifs d'aides » avec les extensions suivantes :

- **ExteExtension d'usage - activation** — Extension créée pour une démonstration, champs non validés - Extension pour définir des aides plus facilement activables
- **Extension d'usage - Pilotage** — Extension créée pour une démonstration, champs non validés
- **Professionnels Extension** — Extension for business professionals (entreprises, indépendants) beneficiaries

> 📖 **À propos** — Ce schéma fait partie d'un ensemble de schémas décrivant les dispositifs d'aides selon leur cible et pour différents usages. Pour le contexte et la finalité de l'ensemble, consultez la documentation principale.

## Champs (34)

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
| `budget_total_alloue` | Budget total alloué | number | Non |
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
