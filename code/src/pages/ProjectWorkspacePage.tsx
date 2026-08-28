import { useParams, Link } from 'react-router-dom';
import { GitBranch, Server, ScrollText, BarChart2, ChevronRight } from 'lucide-react';
import { useProject } from '@/domain/projects/queries';
import ProjectWorkspace from '@/features/project-workspace/ProjectWorkspace';
import styles from './ProjectWorkspacePage.module.scss';

const STRINGS = {
  projects: 'Projets',
  deepLinks: 'Vue détaillée',
  topology: 'Topologie',
  services: 'Services',
  logs: 'Logs',
  metrics: 'Métriques',
};

export default function ProjectWorkspacePage() {
  const { projectId } = useParams<{ projectId?: string }>();
  const { data: project } = useProject(projectId ?? '');

  if (!projectId) return null;

  return (
    <div className={styles.page}>
      {/* Breadcrumb */}
      <nav className={styles.breadcrumb} aria-label="Fil d'Ariane">
        <Link to="/projects" className={styles.breadcrumbLink}>
          {STRINGS.projects}
        </Link>
        <ChevronRight size={14} aria-hidden="true" className={styles.sep} />
        <span className={styles.breadcrumbCurrent}>{project?.name ?? projectId}</span>
      </nav>

      {/* Deep-link bar to legacy views */}
      <div className={styles.deepLinks} aria-label={STRINGS.deepLinks}>
        <Link to={`/projects/${projectId}/topology`} className={styles.deepLink}>
          <GitBranch size={13} aria-hidden="true" /> {STRINGS.topology}
        </Link>
        <Link to={`/projects/${projectId}/services`} className={styles.deepLink}>
          <Server size={13} aria-hidden="true" /> {STRINGS.services}
        </Link>
        <Link to={`/projects/${projectId}/logs`} className={styles.deepLink}>
          <ScrollText size={13} aria-hidden="true" /> {STRINGS.logs}
        </Link>
        <Link to={`/projects/${projectId}/metrics`} className={styles.deepLink}>
          <BarChart2 size={13} aria-hidden="true" /> {STRINGS.metrics}
        </Link>
      </div>

      {/* Workspace fills remaining height */}
      <div className={styles.workspaceWrap}>
        <ProjectWorkspace projectId={projectId} />
      </div>
    </div>
  );
}
