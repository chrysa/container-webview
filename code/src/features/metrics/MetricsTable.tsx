import type { ServiceMetrics } from '@/types/api'

const STATUS_VARIANT: Record<string, string> = {
  running: 'bg-success',
  exited: 'bg-danger',
  paused: 'bg-warning text-dark',
  restarting: 'bg-warning text-dark',
}

export function MetricsTable({ metrics }: { readonly metrics: ServiceMetrics[] }) {
  if (metrics.length === 0) {
    return <p className="text-muted">Aucune métrique disponible.</p>
  }
  return (
    <div className="table-responsive">
      <table className="table table-sm table-hover align-middle">
        <thead className="table-dark">
          <tr>
            <th>Service</th><th>Statut</th><th>CPU %</th>
            <th>RAM Mo</th><th>RAM %</th><th>↓ Réseau</th><th>↑ Réseau</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((m) => (
            <tr key={m.service}>
              <td><strong>{m.service}</strong></td>
              <td>
                <span className={`badge ${STATUS_VARIANT[m.status] ?? 'bg-secondary'}`}>
                  {m.status}
                </span>
              </td>
              <td>{m.cpu_percent.toFixed(1)} %</td>
              <td>{m.mem_usage_mb.toFixed(0)}</td>
              <td>{m.mem_percent.toFixed(1)} %</td>
              <td>{m.net_rx_mb.toFixed(2)} Mo</td>
              <td>{m.net_tx_mb.toFixed(2)} Mo</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
