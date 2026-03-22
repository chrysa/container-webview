export function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="alert alert-danger" role="alert">
      <strong>Erreur :</strong> {message}
    </div>
  )
}
