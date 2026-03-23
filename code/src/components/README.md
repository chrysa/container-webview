# src/components

Composants React réutilisables, sans logique métier. Organisés par rôle technique.

## Structure

```
components/
├── forms/
│   └── LoginForm.tsx      # Formulaire de connexion
├── layouts/
│   ├── Layout.tsx          # Gabarit principal (AppHeader + <Outlet />)
│   ├── AppHeader.tsx       # Barre de navigation (nom utilisateur, déconnexion)
│   ├── ProtectedRoute.tsx  # Redirige vers /login si non authentifié
│   └── PublicRoute.tsx     # Redirige vers / si déjà authentifié
├── loaders/
│   └── GlobalLoader.tsx    # Overlay de chargement plein écran (Suspense fallback)
└── ui/
    └── index.ts            # Exports : LoadingSpinner, ErrorAlert, GlobalLoader
```

## Conventions

- Props toujours `readonly`.
- Pas d'appels API directs — utiliser les hooks React Query dans les pages/features.
- Pas d'état global — les composants reçoivent leurs données par props.
