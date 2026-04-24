import { Moon, Sun, LogOut, ChevronRight, Container } from 'lucide-react';
import { Link, useMatches } from 'react-router-dom';
import { useTheme } from '@/hooks/useTheme';
import { useAuth } from '@/hooks/useAuth';
import { useProject } from '@/domain/projects/queries';
import styles from './Header.module.scss';

const ROUTE_LABELS: Record<string, string> = {
  projects: 'Projets',
  topology: 'Topologie',
  services: 'Services',
  logs: 'Logs',
  metrics: 'Métriques',
  alerts: 'Alertes',
};

function Breadcrumb() {
  const matches = useMatches();
  const projectIdMatch = matches.find((m) => (m.params as Record<string, string>).projectId);
  const projectId = (projectIdMatch?.params as Record<string, string> | undefined)?.projectId;
  const { data: project } = useProject(projectId ?? '');

  const lastPathname = matches.at(-1)?.pathname ?? '';
  const segments = lastPathname.split('/').filter((s): s is string => s.length > 0);
  const lastSegment = segments.at(-1);
  const pageLabel = lastSegment && lastSegment !== projectId ? (ROUTE_LABELS[lastSegment] ?? lastSegment) : null;

  if (!pageLabel) return null;

  const crumbs: { label: string; to?: string }[] = projectId
    ? [
        { label: 'Projets', to: '/projects' },
        { label: project?.name ?? projectId, to: `/projects/${projectId}/topology` },
        { label: pageLabel },
      ]
    : [{ label: pageLabel }];

  if (crumbs.length <= 1) return null;

  return (
    <nav className={styles.breadcrumb} aria-label="Fil d'Ariane">
      {crumbs.map((c, i) => (
        <span key={c.label} className={styles.crumbItem}>
          {i > 0 && <ChevronRight size={12} className={styles.crumbSep} />}
          {c.to && i < crumbs.length - 1 ? (
            <Link to={c.to} className={styles.crumbLink}>{c.label}</Link>
          ) : (
            <span className={styles.crumbCurrent}>{c.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}

export default function Header() {
  const { theme, setTheme } = useTheme();
  const { username, logout } = useAuth();

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <span className={styles.brand}><Container size={20} /> Docker Overview</span>
        <Breadcrumb />
      </div>
      <div className={styles.right}>
        <span className={styles.username}>{username}</span>
        <button
          className={styles.iconBtn}
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          title="Changer le thème"
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
        </button>
        <button className={styles.iconBtn} onClick={logout} title="Se déconnecter">
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
