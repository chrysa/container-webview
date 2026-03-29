import { useQuery } from '@tanstack/react-query'
import { ProjectCard } from '@/features/projects/ProjectCard'
import { AlertsPanel } from '@/features/alerts/AlertsPanel'
import { LoadingSpinner, ErrorAlert } from '@/components/ui'
import { projectService } from '@/api/docker/projectService'
import { alertsService } from '@/api/docker/alertsService'

export function DashboardPage() {
  const {
    data: projectsResult,
    isLoading: projectsLoading,
    error: projectsError,
  } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectService.listAll(),
  })

  const { data: alertsResult } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsService.getAll(),
    refetchInterval: 30_000,
  })

  const projects = projectsResult?.ok ? projectsResult.data : []
  const alerts = alertsResult?.ok ? alertsResult.data : []

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="h4 mb-0">Projets Compose</h2>
        <span className="badge bg-primary fs-6">{projects.length} projet(s)</span>
      </div>

      {alerts.length > 0 && (
        <div className="mb-4">
          <h3 className="h6 text-muted mb-2">Alertes</h3>
          <AlertsPanel alerts={alerts} />
        </div>
      )}

      {projectsLoading && <LoadingSpinner />}
      {projectsError && <ErrorAlert message="Impossible de charger les projets." />}
      {projectsResult && !projectsResult.ok && <ErrorAlert message={projectsResult.error.message} />}

      <div className="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
        {projects.map((project) => (
          <div key={project.id} className="col">
            <ProjectCard project={project} />
          </div>
        ))}
        {!projectsLoading && projects.length === 0 && (
          <div className="col-12">
            <div className="alert alert-info">
              Aucun projet Docker Compose trouvé dans le répertoire configuré.
            </div>
          </div>
        )}
      </div>
    </>
  )
}
