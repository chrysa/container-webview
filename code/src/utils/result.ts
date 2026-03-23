/** Résultat typé sans try/catch. Utiliser `.ok` comme discriminant. */
export type Result<T, E = Error> = { ok: true; data: T } | { ok: false; error: E }

export const ok = <T>(data: T): Result<T> => ({ ok: true, data })
export const err = <T = never>(error: Error): Result<T> => ({ ok: false, error })
