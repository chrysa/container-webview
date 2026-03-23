import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { MetricsTable } from '@/features/metrics/MetricsTable'
import { AlertsPanel } from '@/features/alerts/AlertsPanel'
import { LoadingSpinner, ErrorAlert } from '@/components/ui'
import { projectService } from '@/api/docker/projectService'
import { metricsService } from '@/api/docker/metricsService'
import { alertsService } from '@/api/docker/alertsService'
import { ROUTES } from '@/constants/routes'

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: projectResult, isLoading, error } = useQuery({
    queryKey: ['projects', id],
    queryFn: () => projectService.getById(id ?? ''),
    enabled: Boolean(id),
  })

  const { data: metricsResult } = useQuery({
    queryKey: ['metrics', id],
    queryFn: () => metricsService.getProjectMetrics(id ?? ''),
    enabled: Boolean(id),
    refetchInterval: 10_000,
  })

  const { data: alertsResult } = useQuery({
    queryKey: ['alerts', id],
    queryFn: () => alertsService.getForProject(id ?? ''),
    enabled: Boolean(id),
    refetchInterval: 30_000,
  })

  const project = projectResult?.ok ? projectResult.data : null
  const metrics = metricsResult?.ok ? metricsResult.data : []
  const alerts = alertsResult?.ok ? alertsResult.data : []

  return (
    <>
      <Link to={ROUTES.HOME} className="btn btn-sm btn-outline-secondary mb-3">
        ← Retour
      </Link>

      {isLoading && <LoadingSpinner />}
      {error && <ErrorAlert message="Impossible de charger le projet." />}
      {projectResult && !projectResult.ok && <ErrorAlert message={projectResult.error.message} />}

      {project && (
        <>
          <div className="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h2 className="h4 mb-1">{project.name}</h2>
              <code className="text-muted small">{project.compose_file}</code>
            </div>
            <div className="d-flex gap-2">
              <span className="badge bg-primary">{project.services.length} services</span>
              <span className="badge bg-secondary">{project.networks.length} réseaux</span>
            </div>
          </div>

          <div className="row g-4">
            <div className="col-12">
              <div className="card">
                <div className="card-header"><strong>Services</strong></div>
                <div className="card-body p-0">
                  <div className="table-responsive">
                    <table className="table table-sm mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Nom</th><th>Image</th><th>Ports</th><th>Réseaux</th>
                        </tr>
                      </thead>
                      <tbody>
                        {project.services.map((svc) => (
                          <tr key={svc.name}>
                            <td><strong>{svc.name}</strong></td>
                            <td><code className="small">{svc.image ?? '—'}</code></td>
                            <td>{svc.ports.join(', ') || '—'}</td>
                            <td>{svc.networks.join(', ') || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="card">
                <div className="card-header"><strong>Métriques en temps réel</strong></div>
                <div className="card-body">
                  <MetricsTable metrics={metrics} />
                </div>
              </div>
            </div>

            <div className="col-12">
              <div className="card">
                <div className="card-header"><strong>Alertes</strong></div>
                <div className="card-body">
                  <AlertsPanel alerts={alerts} />
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  )
}
