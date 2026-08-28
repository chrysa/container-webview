import { Link } from 'react-router-dom';
import { GitBranch, Server, ScrollText, BarChart2, Package, FileText, Network, AlertCircle } from 'lucide-react';
import { useProjects } from '@/domain/projects/queries';
import { useMetrics } from '@/domain/metrics/queries';
import { useAlerts } from '@/domain/alerts/queries';
import type { Project } from '@/domain/projects/types';
import { deriveProjectHealth, deriveServiceHealth } from '@/domain/health/deriveHealth';
import HealthBadge from '@/features/project-workspace/HealthBadge';
import styles from './Projects.module.scss';

// ── string constants ──────────────────────────────────────────────────────────

const STRINGS = {
  heading: 'Projets',
  loading: 'Chargement des projets…',
  errorMsg: 'Impossible de charger les projets.',
  emptyMsg: 'Aucun projet détecté.',
  emptyHint: 'Montez un répertoire contenant vos fichiers',
  services: (n: number) => `${n} service${n > 1 ? 's' : ''}`,
  networks: (n: number) => `${n} réseau${n > 1 ? 'x' : ''}`,
  more: (n: number) => `+${n} autres…`,
  openWorkspace: 'Ouvrir le workspace',
  links: {
    topology: 'Topologie',
    services: 'Services',
    logs: 'Logs',
    metrics: 'Métriques',
  },
};

export default function Projects() {
  const { data: projects = [], isLoading, error } = useProjects();

  if (isLoading)
    return (
      <div className={styles.state} role="status" aria-live="polite">
        {STRINGS.loading}
      </div>
    );

  if (error) {
    return (
      <div className={styles.error} role="alert">
        <AlertCircle size={32} />
        <p>{STRINGS.errorMsg}</p>
        <p className={styles.hint}>{error.message}</p>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className={styles.wrapper}>
        <h1 className={styles.heading}>{STRINGS.heading}</h1>
        <div data-testid="empty-state" className={styles.empty} role="status">
          <p>{STRINGS.emptyMsg}</p>
          <p className={styles.hint}>
            {STRINGS.emptyHint} <code>docker-compose.yml</code> dans <code>/projects</code>.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>{STRINGS.heading}</h1>
      <div className={styles.grid}>
        {projects.map((p) => (
          <ProjectCard key={p.id} project={p} />
        ))}
      </div>
    </div>
  );
}

// ── ProjectCard (separate component so each card fetches its own metrics/alerts)
// This avoids prop-drilling and keeps the parent Projects component thin.

interface ProjectCardProps {
  readonly project: Project;
}

function ProjectCard({ project: p }: ProjectCardProps) {
  const { data: metrics } = useMetrics(p.id);
  const { data: alerts } = useAlerts();

  // Filter alerts to this project
  const projectAlerts = (alerts ?? []).filter((a) => a.project === p.name);

  const projectHealth = deriveProjectHealth(
    p.services.map((s) => s.name),
    metrics,
    projectAlerts
  );

  return (
    <div data-testid="project-card" className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.cardIcon}>
          <Package size={20} />
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h2 className={styles.cardTitle}>{p.name}</h2>
          <p className={styles.cardSub}>{STRINGS.services(p.services.length)}</p>
        </div>
        {/* Project-level derived health badge */}
        <HealthBadge status={projectHealth} />
      </div>

      <div className={styles.meta}>
        <span className={styles.metaItem}>
          <FileText size={12} /> {p.compose_file}
        </span>
        <span className={styles.metaItem}>
          <Network size={12} /> {STRINGS.networks(p.networks.length)}
        </span>
      </div>

      <ul className={styles.services}>
        {p.services.slice(0, 5).map((s) => {
          const svcHealth = deriveServiceHealth(s.name, metrics, projectAlerts);
          return (
            <li key={s.name} className={styles.service}>
              <HealthBadge status={svcHealth} compact />
              {s.name}
              {s.image && <span className={styles.image}> — {s.image}</span>}
            </li>
          );
        })}
        {p.services.length > 5 && <li className={styles.more}>{STRINGS.more(p.services.length - 5)}</li>}
      </ul>

      <div className={styles.links}>
        {/* Primary link → project workspace */}
        <Link to={`/projects/${p.id}`} className={`${styles.link} ${styles.linkPrimary}`}>
          <Server size={14} /> {STRINGS.openWorkspace}
        </Link>
        <Link to={`/projects/${p.id}/topology`} className={styles.link}>
          <GitBranch size={14} /> {STRINGS.links.topology}
        </Link>
        <Link to={`/projects/${p.id}/services`} className={styles.link}>
          <Server size={14} /> {STRINGS.links.services}
        </Link>
        <Link to={`/projects/${p.id}/logs`} className={styles.link}>
          <ScrollText size={14} /> {STRINGS.links.logs}
        </Link>
        <Link to={`/projects/${p.id}/metrics`} className={styles.link}>
          <BarChart2 size={14} /> {STRINGS.links.metrics}
        </Link>
      </div>
    </div>
  );
}
