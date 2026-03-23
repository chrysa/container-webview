# src/types

Interfaces et types TypeScript partagés à travers l'application.

## Fichiers

| Fichier | Contenu |
|---|---|
| `api.ts` | Modèles de réponse API (ProjectModel, ServiceMetrics, Alert, TopologyGraph, etc.) + HATEOAS |
| `auth.ts` | `AuthContextType` — interface du contexte d'authentification |

## Conventions

- Pas de logique dans ce dossier — types uniquement.
- Les types HATEOAS (`HateoasLink`, `WithLinks`) sont dans `api.ts`.
- Les interfaces de contexte React sont dans leur propre fichier (ex. `auth.ts`).
