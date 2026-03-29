# src/stores

Stores vanilla (sans React) pour l'état partagé entre logique non-React et composants.

## Fichiers

| Store | Rôle |
|---|---|
| `loadingStore.ts` | Compteur de requêtes HTTP en cours — publication/abonnement |

## Pattern

```ts
// S'abonner
const unsubscribe = loadingStore.subscribe((isLoading) => { ... })

// Dans le client HTTP
loadingStore.start()   // avant fetch
loadingStore.complete() // après fetch
```

## Conventions

- Pas de dépendance à React — utilisable en dehors des composants.
- Pattern pub/sub simple avec `Set<Listener>`.
