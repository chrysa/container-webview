export function GlobalLoader() {
  return (
    <div
      className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
      style={{ background: 'rgba(0,0,0,0.3)', zIndex: 9999 }}
    >
      <div className="spinner-border text-light" style={{ width: '3rem', height: '3rem' }} aria-live="polite" aria-busy="true">
        <span className="visually-hidden">Chargement…</span>
      </div>
    </div>
  )
}
