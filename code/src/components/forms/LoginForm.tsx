import { useState } from 'react'
import type { FormEvent } from 'react'
import { useAuth } from '@/hooks/useAuth'

interface LoginFormProps {
  readonly onSuccess: () => void
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await login(username, password)
      onSuccess()
    } catch {
      setError('Identifiants invalides. Veuillez réessayer.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      {error && <div className="alert alert-danger py-2">{error}</div>}
      <div className="mb-3">
        <label htmlFor="username" className="form-label">Utilisateur</label>
        <input
          id="username"
          type="text"
          className="form-control"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />
      </div>
      <div className="mb-4">
        <label htmlFor="password" className="form-label">Mot de passe</label>
        <input
          id="password"
          type="password"
          className="form-control"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </div>
      <button type="submit" className="btn btn-primary w-100" disabled={isSubmitting}>
        {isSubmitting
          ? <><span className="spinner-border spinner-border-sm me-2" />Connexion…</>
          : 'Se connecter'}
      </button>
    </form>
  )
}
