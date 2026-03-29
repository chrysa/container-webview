import { Link } from "react-router-dom";
import { GitBranch, Server, ScrollText, BarChart2 } from "lucide-react";
import { useProjects } from "@/domain/projects/queries";
import styles from "./Projects.module.scss";

export default function Projects() {
  const { data: projects = [], isLoading } = useProjects();

  if (isLoading) return <div className={styles.state}>Chargement des projets…</div>;

  if (projects.length === 0) {
    return (
      <div className={styles.empty}>
        <p>Aucun projet détecté.</p>
        <p className={styles.hint}>
          Montez un répertoire contenant vos fichiers <code>docker-compose.yml</code> dans <code>/projects</code>.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Projets</h1>
      <div className={styles.grid}>
        {projects.map((p) => (
          <div key={p.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>📦</span>
              <div>
                <h2 className={styles.cardTitle}>{p.name}</h2>
                <p className={styles.cardSub}>{p.services.length} service{p.services.length > 1 ? "s" : ""}</p>
              </div>
            </div>

            <div className={styles.meta}>
              <span className={styles.metaItem}>📄 {p.compose_file}</span>
              <span className={styles.metaItem}>🌐 {p.networks.length} réseau{p.networks.length > 1 ? "x" : ""}</span>
            </div>

            <ul className={styles.services}>
              {p.services.slice(0, 5).map((s) => (
                <li key={s.name} className={styles.service}>
                  <span className={styles.dot} />
                  {s.name}
                  {s.image && <span className={styles.image}> — {s.image}</span>}
                </li>
              ))}
              {p.services.length > 5 && (
                <li className={styles.more}>+{p.services.length - 5} autres…</li>
              )}
            </ul>

            <div className={styles.links}>
              <Link to={`/projects/${p.id}/topology`} className={styles.link}>
                <GitBranch size={14} /> Topologie
              </Link>
              <Link to={`/projects/${p.id}/services`} className={styles.link}>
                <Server size={14} /> Services
              </Link>
              <Link to={`/projects/${p.id}/logs`} className={styles.link}>
                <ScrollText size={14} /> Logs
              </Link>
              <Link to={`/projects/${p.id}/metrics`} className={styles.link}>
                <BarChart2 size={14} /> Métriques
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
