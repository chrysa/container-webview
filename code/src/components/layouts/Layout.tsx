import { Outlet } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { AppHeader } from './AppHeader'

export default function Layout() {
  const { isAuthenticated } = useAuth()
  return (
    <div className="d-flex flex-column min-vh-100 bg-light">
      {isAuthenticated && <AppHeader />}
      <main className="container-fluid py-4 flex-grow-1">
        <Outlet />
      </main>
    </div>
  )
}
