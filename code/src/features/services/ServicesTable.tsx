/**
 * ServicesTable — flat table view of a project's services.
 * Phase-4 IA pass changes:
 *   - FIX: JSX key moved from inner <tr> to the wrapping Fragment (was on wrong element)
 *   - ADDED: derived health badge per row (via useMetrics + useAlerts)
 *   - ADDED: aria-label on icon-only lifecycle buttons
 *   - ADDED: aria-expanded on the env expand toggle
 *   - ADDED: aria-live on empty / loading states
 *   - ADDED: designed empty state with role="status"
 *   - PROMOTED: Restart / Start as primary action; Stop/Pause demoted to secondary
 */

import { Fragment, useState } from 'react';
import { Play, Square, RotateCcw, Pause, ChevronDown, ChevronUp, Eye, EyeOff, AlertCircle, Server } from 'lucide-react';
import { useProject } from '@/domain/projects/queries';
import { useMetrics } from '@/domain/metrics/queries';
import { useAlerts } from '@/domain/alerts/queries';
import { useServiceAction } from '@/domain/lifecycle/queries';
import { useToast } from '@/components/feedback/Toast';
import { deriveServiceHealth } from '@/domain/health/deriveHealth';
import HealthBadge from '@/features/project-workspace/HealthBadge';
import styles from './ServicesTable.module.scss';

// ── string constants ──────────────────────────────────────────────────────────

const STRINGS = {
  loading: 'Chargement…',
  error: 'Erreur lors du chargement des services.',
  notFound: 'Projet introuvable.',
  empty: 'Aucun service trouvé.',
  emptyHint: 'Ce projet ne déclare aucun service dans son fichier Compose.',
  colService: 'Service',
  colHealth: 'Santé',
  colImage: 'Image',
  colPorts: 'Ports',
  colNetworks: 'Réseaux',
  colActions: 'Actions',
  restart: 'Redémarrer',
  start: 'Démarrer',
  stop: 'Arrêter',
  pause: 'Mettre en pause',
  expandDetail: 'Afficher les détails',
  collapseDetail: 'Masquer les détails',
  envLabel: "Variables d'environnement :",
  envShow: 'Afficher les valeurs sensibles',
  envHide: 'Masquer les valeurs sensibles',
  volumes: 'Volumes :',
  dependsOn: 'Dépend de :',
};

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
  const { data: metrics } = useMetrics(projectId);
  const { data: alerts } = useAlerts();
  const { mutate: doAction, isPending } = useServiceAction(projectId);
  const { toast } = useToast();
  const [pendingService, setPendingService] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [revealedEnvs, setRevealedEnvs] = useState<Set<string>>(new Set());

  if (isLoading) {
    return (
      <div className={styles.state} role="status" aria-live="polite">
        {STRINGS.loading}
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState} role="alert">
        <AlertCircle size={20} aria-hidden="true" />
        <span>{STRINGS.error}</span>
      </div>
    );
  }

  if (!project) {
    return (
      <div className={styles.state} role="status" aria-live="polite">
        {STRINGS.notFound}
      </div>
    );
  }

  if (project.services.length === 0) {
    return (
      <div className={styles.emptyState} role="status" aria-live="polite">
        <Server size={28} aria-hidden="true" />
        <p>{STRINGS.empty}</p>
        <p className={styles.emptyHint}>{STRINGS.emptyHint}</p>
      </div>
    );
  }

  function handleAction(service: string, action: string, label: string) {
    setPendingService(service);
    doAction(
      { service, action },
      {
        onSuccess: () => {
          toast(`${label} de ${service} effectué.`, 'success');
          setPendingService(null);
        },
        onError: (err) => {
          toast(`Échec ${label} de ${service} : ${err.message}`, 'error');
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

  const projectAlerts = (alerts ?? []).filter((a) => a.project === project.name);
  const isBusy = (svcName: string) => pendingService === svcName || isPending;

  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>{STRINGS.colService}</th>
            <th>{STRINGS.colHealth}</th>
            <th>{STRINGS.colImage}</th>
            <th>{STRINGS.colPorts}</th>
            <th>{STRINGS.colNetworks}</th>
            <th>{STRINGS.colActions}</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {project.services.map((svc) => {
            const health = deriveServiceHealth(svc.name, metrics, projectAlerts);
            const isExpanded = expanded === svc.name;
            const isRunning = health === 'running';

            // FIX: key is on the Fragment wrapper (was incorrectly on the inner <tr>)
            return (
              <Fragment key={svc.name}>
                <tr className={styles.row}>
                  <td>
                    <span className={styles.name}>{svc.name}</span>
                  </td>
                  <td>
                    <HealthBadge status={health} />
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
                      {/* PRIMARY action: Restart if running, Start if stopped */}
                      {isRunning ? (
                        <button
                          className={`${styles.btn} ${styles.restart} ${styles.btnPrimary}`}
                          onClick={() => handleAction(svc.name, 'restart', STRINGS.restart)}
                          disabled={isBusy(svc.name)}
                          aria-label={`${STRINGS.restart} ${svc.name}`}
                          title={STRINGS.restart}
                        >
                          <RotateCcw size={14} aria-hidden="true" />
                        </button>
                      ) : (
                        <button
                          className={`${styles.btn} ${styles.start} ${styles.btnPrimary}`}
                          onClick={() => handleAction(svc.name, 'start', STRINGS.start)}
                          disabled={isBusy(svc.name)}
                          aria-label={`${STRINGS.start} ${svc.name}`}
                          title={STRINGS.start}
                        >
                          <Play size={14} aria-hidden="true" />
                        </button>
                      )}

                      {/* SECONDARY: Stop */}
                      <button
                        className={`${styles.btn} ${styles.stop}`}
                        onClick={() => handleAction(svc.name, 'stop', STRINGS.stop)}
                        disabled={isBusy(svc.name) || !isRunning}
                        aria-label={`${STRINGS.stop} ${svc.name}`}
                        title={STRINGS.stop}
                      >
                        <Square size={14} aria-hidden="true" />
                      </button>

                      {/* SECONDARY: Pause */}
                      <button
                        className={`${styles.btn} ${styles.pause}`}
                        onClick={() => handleAction(svc.name, 'pause', STRINGS.pause)}
                        disabled={isBusy(svc.name) || !isRunning}
                        aria-label={`${STRINGS.pause} ${svc.name}`}
                        title={STRINGS.pause}
                      >
                        <Pause size={14} aria-hidden="true" />
                      </button>
                    </div>
                  </td>
                  <td>
                    <button
                      className={styles.expandBtn}
                      onClick={() => setExpanded(isExpanded ? null : svc.name)}
                      aria-expanded={isExpanded}
                      aria-label={
                        isExpanded ? `${STRINGS.collapseDetail} ${svc.name}` : `${STRINGS.expandDetail} ${svc.name}`
                      }
                    >
                      {isExpanded ? (
                        <ChevronUp size={16} aria-hidden="true" />
                      ) : (
                        <ChevronDown size={16} aria-hidden="true" />
                      )}
                    </button>
                  </td>
                </tr>

                {isExpanded && (
                  <tr className={styles.detailRow}>
                    <td colSpan={7}>
                      <div className={styles.detail}>
                        {svc.volumes.length > 0 && (
                          <div>
                            <strong>{STRINGS.volumes}</strong>{' '}
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
                              <strong>{STRINGS.envLabel}</strong>
                              <button
                                className={styles.revealBtn}
                                onClick={() => toggleRevealEnv(svc.name)}
                                aria-label={revealedEnvs.has(svc.name) ? STRINGS.envHide : STRINGS.envShow}
                                title={revealedEnvs.has(svc.name) ? STRINGS.envHide : STRINGS.envShow}
                              >
                                {revealedEnvs.has(svc.name) ? (
                                  <EyeOff size={12} aria-hidden="true" />
                                ) : (
                                  <Eye size={12} aria-hidden="true" />
                                )}
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
                            <strong>{STRINGS.dependsOn}</strong>{' '}
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
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
