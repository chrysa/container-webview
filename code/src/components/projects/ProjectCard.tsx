import { Link } from 'react-router-dom'
import { ROUTES } from '../../constants/config'
import type { ProjectModel } from '../../types/api'

export function ProjectCard({ project }: { project: ProjectModel }) {
  return (
    <div className="card h-100 shadow-sm">
      <div className="card-body">
        <h5 className="card-title">{project.name}</h5>
        <p className="card-text text-muted small mb-2">
          <code>{project.compose_file}</code>
        </p>
        <div className="d-flex gap-2 mb-3">
          <span className="badge bg-primary">{project.services.length} services</span>
          <span className="badge bg-secondary">{project.networks.length} réseaux</span>
        </div>
        <div className="d-flex flex-wrap gap-1">
          {project.services.map((svc) => (
            <span key={svc.name} className="badge bg-light text-dark border">{svc.name}</span>
          ))}
        </div>
      </div>
      <div className="card-footer bg-transparent">
        <Link to={ROUTES.projectDetail(project.id)} className="btn btn-outline-primary btn-sm w-100">
          Voir le détail →
        </Link>
      </div>
    </div>
  )
}
