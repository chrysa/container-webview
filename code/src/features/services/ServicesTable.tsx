import { useState } from 'react';
import { Play, Square, RotateCcw, Pause, ChevronDown, ChevronUp, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useProject } from '@/domain/projects/queries';
import { useServiceAction } from '@/domain/lifecycle/queries';
import { useToast } from '@/components/feedback/Toast';
import styles from './ServicesTable.module.scss';

const SENSITIVE_KEY = /password|secret|token|key|pwd|pass/i;

function maskEnvValue(key: string, value: string, revealed: boolean): string {
  if (revealed || !SENSITIVE_KEY.test(key)) return value;
  return '••••••••';
}

interface Props {
  readonly projectId: string;
}

export default function ServicesTable({ projectId }: Readonly<Props>) {
  const { data: project, isLoading, error } = useProject(projectId);
  const { mutate: doAction } = useServiceAction(projectId);
  const { toast } = useToast();
  const [pendingService, setPendingService] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [revealedEnvs, setRevealedEnvs] = useState<Set<string>>(new Set());

  if (isLoading) return <div className={styles.state}>Chargement…</div>;
  if (error)
    return (
      <div className={styles.errorState}>
        <AlertCircle size={20} />
        <span>Erreur lors du chargement des services.</span>
      </div>
    );
  if (!project) return <div className={styles.state}>Projet introuvable.</div>;

  function handleAction(service: string, action: string) {
    setPendingService(service);
    doAction(
      { service, action },
      {
        onSuccess: () => {
          toast(`${action} de ${service} effectué.`, 'success');
          setPendingService(null);
        },
        onError: (err) => {
          toast(`Échec ${action} de ${service} : ${err.message}`, 'error');
          setPendingService(null);
        },
      }
    );
  }

  function toggleRevealEnv(svcName: string) {
    setRevealedEnvs((prev) => {
      const next = new Set(prev);
      if (next.has(svcName)) next.delete(svcName);
      else next.add(svcName);
      return next;
    });
  }

  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Service</th>
            <th>Image</th>
            <th>Ports</th>
            <th>Réseaux</th>
            <th>Actions</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {project.services.map((svc) => (
            <>
              <tr key={svc.name} className={styles.row}>
                <td>
                  <span className={styles.name}>{svc.name}</span>
                </td>
                <td className={styles.image}>{svc.image || '—'}</td>
                <td>
                  {svc.ports.length > 0
                    ? svc.ports.map((p) => (
                        <span key={p} className={styles.badge}>
                          {p}
                        </span>
                      ))
                    : '—'}
                </td>
                <td>
                  {svc.networks.map((n) => (
                    <span key={n} className={styles.badge}>
                      {n}
                    </span>
                  ))}
                </td>
                <td>
                  <div className={styles.actions}>
                    <button
                      className={`${styles.btn} ${styles.start}`}
                      onClick={() => handleAction(svc.name, 'start')}
                      disabled={pendingService === svc.name}
                      title="Démarrer"
                    >
                      <Play size={14} />
                    </button>
                    <button
                      className={`${styles.btn} ${styles.stop}`}
                      onClick={() => handleAction(svc.name, 'stop')}
                      disabled={pendingService === svc.name}
                      title="Arrêter"
                    >
                      <Square size={14} />
                    </button>
                    <button
                      className={`${styles.btn} ${styles.restart}`}
                      onClick={() => handleAction(svc.name, 'restart')}
                      disabled={pendingService === svc.name}
                      title="Redémarrer"
                    >
                      <RotateCcw size={14} />
                    </button>
                    <button
                      className={`${styles.btn} ${styles.pause}`}
                      onClick={() => handleAction(svc.name, 'pause')}
                      disabled={pendingService === svc.name}
                      title="Mettre en pause"
                    >
                      <Pause size={14} />
                    </button>
                  </div>
                </td>
                <td>
                  <button
                    className={styles.expandBtn}
                    onClick={() => setExpanded(expanded === svc.name ? null : svc.name)}
                  >
                    {expanded === svc.name ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </td>
              </tr>
              {expanded === svc.name && (
                <tr className={styles.detailRow}>
                  <td colSpan={6}>
                    <div className={styles.detail}>
                      {svc.volumes.length > 0 && (
                        <div>
                          <strong>Volumes :</strong>{' '}
                          {svc.volumes.map((v) => (
                            <span key={v} className={styles.badge}>
                              {v}
                            </span>
                          ))}
                        </div>
                      )}
                      {Object.keys(svc.environment).length > 0 && (
                        <div>
                          <div className={styles.envHeader}>
                            <strong>Variables d&apos;environnement :</strong>
                            <button
                              className={styles.revealBtn}
                              onClick={() => toggleRevealEnv(svc.name)}
                              title={
                                revealedEnvs.has(svc.name)
                                  ? 'Masquer les valeurs sensibles'
                                  : 'Afficher les valeurs sensibles'
                              }
                            >
                              {revealedEnvs.has(svc.name) ? <EyeOff size={12} /> : <Eye size={12} />}
                            </button>
                          </div>
                          <pre className={styles.env}>
                            {Object.entries(svc.environment)
                              .map(([k, v]) => `${k}=${maskEnvValue(k, v, revealedEnvs.has(svc.name))}`)
                              .join('\n')}
                          </pre>
                        </div>
                      )}
                      {svc.depends_on.length > 0 && (
                        <div>
                          <strong>Dépend de :</strong>{' '}
                          {svc.depends_on.map((d) => (
                            <span key={d} className={styles.badge}>
                              {d}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}
