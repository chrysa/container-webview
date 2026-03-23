# src/constants

Constantes applicatives centralisées. **Aucune logique**, valeurs uniquement.

## Fichiers

| Fichier | Contenu |
|---|---|
| `api.ts` | `API_BASE_URL`, `API_ROUTES` (toutes les routes backend) |
| `app.ts` | `DOM_EVENTS`, `HTTP_HEADERS`, `HTTP_HEADER_VALUES`, `ERROR_MESSAGES` |
| `routes.ts` | `ROUTES` (toutes les routes frontend React Router) |
| `storage.ts` | `STORAGE_KEYS` (clés localStorage) |
| `config.ts` | ⚠️ Déprécié — re-exporte les autres fichiers pour compatibilité |

## Règle

Ne jamais importer depuis `config.ts` dans le nouveau code. Importer directement depuis le fichier spécialisé.
