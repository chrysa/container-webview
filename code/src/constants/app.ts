/** Événements DOM émis par l'application. */
export const DOM_EVENTS = {
  AUTH_UNAUTHORIZED: 'auth:unauthorized',
} as const

/** Clés des headers HTTP. */
export const HTTP_HEADERS = {
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
} as const

/** Valeurs des headers HTTP. */
export const HTTP_HEADER_VALUES = {
  JSON: 'application/json',
  FORM_URLENCODED: 'application/x-www-form-urlencoded',
  BEARER_PREFIX: 'Bearer',
} as const

/** Messages d'erreur internes (non traduits). */
export const ERROR_MESSAGES = {
  UNAUTHORIZED: 'Unauthorized',
  NETWORK_ERROR: 'Erreur réseau — vérifiez votre connexion.',
  HTTP_STATUS: (status: number) => `Erreur HTTP ${status}`,
} as const
