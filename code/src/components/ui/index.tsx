export function LoadingSpinner() {
  return (
    <div className="d-flex justify-content-center align-items-center py-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Chargement…</span>
      </div>
    </div>
  )
}

export function ErrorAlert({ message }: { readonly message: string }) {
  return (
    <div className="alert alert-danger" role="alert">
      <strong>Erreur :</strong> {message}
    </div>
  )
}

export { GlobalLoader } from '../loaders/GlobalLoader'
