# src/providers

Providers React Context — séparent la définition du contexte de son implémentation.

## Fichiers

| Fichier | Rôle |
|---|---|
| `AuthContext.ts` | Définition du contexte (`createContext`) uniquement |
| `AuthProvider.tsx` | Implémentation : état, effets, callbacks, valeur mémorisée |

## Pattern

```tsx
// AuthContext.ts — contexte seul, sans état
export const AuthContext = createContext<AuthContextType | undefined>(undefined)

// AuthProvider.tsx — logique d'état
export function AuthProvider({ children }) {
  const [token, setToken] = useState(...)
  // ...
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
```

## Conventions

- Séparer `Context.ts` (pas de `.tsx`) de `Provider.tsx` pour éviter les imports circulaires.
- `useAuth()` dans `@/hooks/useAuth.ts` — ne jamais consommer `AuthContext` directement.
- L'événement `auth:unauthorized` (émis par le client HTTP sur les 401) est écouté ici.
