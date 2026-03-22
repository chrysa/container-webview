import { Link } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { ROUTES } from '../../constants/config'

export function Navbar() {
  const { username, logout } = useAuth()
  return (
    <nav className="navbar navbar-dark bg-dark px-3">
      <Link className="navbar-brand fw-bold" to={ROUTES.DASHBOARD}>
        🐳 Docker Overview
      </Link>
      <div className="d-flex align-items-center gap-3">
        <span className="text-secondary small">{username}</span>
        <button className="btn btn-outline-light btn-sm" onClick={logout}>
          Déconnexion
        </button>
      </div>
    </nav>
  )
}
