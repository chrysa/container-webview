import type { Alert } from '@/types/api'

const LEVEL_CLASS: Record<string, string> = {
  info: 'alert-info',
  warning: 'alert-warning',
  critical: 'alert-danger',
}

export function AlertsPanel({ alerts }: { readonly alerts: Alert[] }) {
  if (alerts.length === 0) {
    return <div className="alert alert-success mb-0">✅ Aucune alerte active.</div>
  }
  return (
    <div className="d-flex flex-column gap-2">
      {alerts.map((alert) => (
        <div key={alert.id} className={`alert ${LEVEL_CLASS[alert.level] ?? 'alert-secondary'} mb-0`}>
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <span className="badge bg-secondary me-2">{alert.level.toUpperCase()}</span>
              <strong>{alert.service}</strong> — {alert.message}
            </div>
            <small className="text-muted ms-3 text-nowrap">
              {new Date(alert.timestamp).toLocaleTimeString()}
            </small>
          </div>
        </div>
      ))}
    </div>
  )
}
