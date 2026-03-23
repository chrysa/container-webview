# src/utils

Utilitaires purs — fonctions sans effet de bord, sans dépendance à React.

## Fichiers

| Fichier | Rôle |
|---|---|
| `result.ts` | Type `Result<T>` — résultat discriminé `{ ok: true, data }` / `{ ok: false, error }` |
| `logger.ts` | Logger minimal — `debug` silencieux en production |

## Pattern Result<T>

```ts
import type { Result } from '@/utils/result'

// Dans un service
async function fetchData(): Promise<Result<string>> {
  const res = await apiClient.get<string>('/endpoint')
  return res // déjà un Result<T>
}

// Dans un composant
const result = await fetchData()
if (!result.ok) {
  console.error(result.error.message)
  return
}
console.log(result.data) // string garanti
```

## Conventions

- Pas de `try/catch` dans les services — le client HTTP gère les erreurs et retourne `Result<T>`.
- `logger.debug()` n'affiche rien en production (`import.meta.env.DEV`).
