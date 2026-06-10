# Dispositifs d'aides pour les professionnels

Extension du schéma dispositif-aide pour la cible 'professionnels'

## Composition

Ce schéma enrichit le socle commun « Dispositifs d'aides » avec les extensions suivantes :

- **Extension du schéma des dispositifs d'aides pour les aides dédiées aux professionnels** — Ajout de champs permettant de préciser l'éligibilité des entreprises aux différents dispositifs d'aides ainsi que les informations administratives nécessaires à leur instruction (base juridique, chaînage avec une demande de paiement).

> 📖 **À propos** — Ce schéma fait partie d'un ensemble de schémas décrivant les dispositifs d'aides selon leur cible et pour différents usages. Pour le contexte et la finalité de l'ensemble, consultez la documentation principale.

## Champs (26)

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
| `base_juridique` | Bases juridiques | string | Non |
| `eligibilite_effectif_minimal` | Éligibilité - Effectif minimal | integer | Non |
| `eligibilite_effectif_maximal` | Éligibilité - Effectif maximal | integer | Non |
| `eligibilite_categorie_taille_entreprise` | Éligibilité - Catégories de taille d'entreprise | string | Non |
| `eligibilite_annees_existence_minimal` | Éligibilité - Nombre d'années d'existence minimal | integer | Non |
| `eligibilite_forme_juridique` | Éligibilité - Formes juridiques éligibles | string | Non |
| `eligibilite_forme_juridique_exclusions` | Éligibilité - Formes juridiques - Exclusions | string | Non |
| `ciblage_secteur_activite` | Secteurs d'activité principalement concernés | string | Oui |
| `ciblage_naf` | Ciblage - NAF | string | Non |
| `ciblage_naf_exclusions` | Ciblage - NAF - Exclusions | string | Non |
| `chainage_paiement` | ID de l'aide dont ce dispositif est la demande de paiement | string | Non |

## Ressources

- Schéma : [`schema.json`](schema.json)
- Exemple valide : [`exemple.csv`](exemple.csv)
