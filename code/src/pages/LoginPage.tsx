import { Navigate, useNavigate } from 'react-router-dom'
import { LoginForm } from '@/components/forms/LoginForm'
import { useAuth } from '@/hooks/useAuth'
import { ROUTES } from '@/constants/routes'

export function LoginPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) return <Navigate to={ROUTES.HOME} replace />

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card shadow" style={{ width: '100%', maxWidth: '420px' }}>
        <div className="card-body p-4">
          <div className="text-center mb-4">
            <span style={{ fontSize: '2.5rem' }}>🐳</span>
            <h1 className="h4 mt-2 mb-0">Docker Overview</h1>
            <p className="text-muted small">Connectez-vous pour continuer</p>
          </div>
          <LoginForm onSuccess={() => navigate(ROUTES.HOME, { replace: true })} />
        </div>
      </div>
    </div>
  )
}
