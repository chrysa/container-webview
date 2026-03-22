import type { ReactNode } from 'react'
import { Navbar } from './Navbar'

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="d-flex flex-column min-vh-100 bg-light">
      <Navbar />
      <main className="container-fluid py-4 flex-grow-1">
        {children}
      </main>
    </div>
  )
}
