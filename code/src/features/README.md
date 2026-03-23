# src/features

Modules fonctionnels — composants React spécifiques à un domaine métier de l'application.

## Structure

```
features/
├── projects/
│   └── ProjectCard.tsx    # Carte d'un projet Compose
├── metrics/
│   └── MetricsTable.tsx   # Tableau de métriques temps réel
├── alerts/
│   └── AlertsPanel.tsx    # Liste des alertes opérationnelles
├── topology/              # (futur) Graphe de topologie des services
└── lifecycle/             # (futur) Contrôles start/stop/restart
```

## Conventions

- Un dossier par domaine fonctionnel.
- Les composants peuvent appeler les hooks React Query via `@/api/docker/`.
- Ne pas importer entre features — passer par les pages si besoin de composition.
