/**
 * ProjectWorkspace — Phase-4 IA pass headline screen.
 *
 * Master/detail layout:
 *   LEFT  — service fleet list (each row: health badge + name + image)
 *   RIGHT — selected service detail (config + sparkline + alerts inline
 *           + lifecycle actions + log link)
 *
 * Health derivation: client-side, from useMetrics + useAlerts.
 * No backend change. See domain/health/deriveHealth.ts for rationale.
 *
 * FOLLOW-UP: backend should expose a first-class service.status field so
 * the project query alone suffices without the metrics dependency.
 */

import { useState, useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Play,
  RotateCcw,
  Square,
  Pause,
  ScrollText,
  AlertTriangle,
  Info,
  XCircle,
  ChevronDown,
  ChevronUp,
  Eye,
  EyeOff,
  Cpu,
  Server,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import { useProject } from '@/domain/projects/queries';
import { useMetrics } from '@/domain/metrics/queries';
import { useAlerts } from '@/domain/alerts/queries';
import { useServiceAction } from '@/domain/lifecycle/queries';
import { useToast } from '@/components/feedback/Toast';
import { deriveServiceHealth } from '@/domain/health/deriveHealth';
import type { HealthStatus } from '@/domain/health/deriveHealth';
import type { Service } from '@/domain/projects/types';
import type { Alert } from '@/domain/alerts/types';
import type { ServiceMetrics } from '@/domain/metrics/types';
import HealthBadge from './HealthBadge';
import ServiceSparkline from './ServiceSparkline';
import styles from './ProjectWorkspace.module.scss';

// ── string constants (i18n-ready: centralised here) ──────────────────────────

const STRINGS = {
  servicesHeader: 'Services',
  noServices: 'Aucun service dans ce projet.',
  noServicesHint: 'Vérifiez votre fichier docker-compose.yml.',
  loadingServices: 'Chargement du projet…',
  errorServices: 'Impossible de charger le projet.',
  selectPrompt: 'Sélectionnez un service',
  selectHint: 'Choisissez un service dans la liste pour voir ses détails.',
  configSection: 'Configuration',
  metricsSection: 'Métriques temps réel',
  alertsSection: 'Alertes',
  logsLink: 'Voir les logs',
  restart: 'Redémarrer',
  start: 'Démarrer',
  stop: 'Arrêter',
  pause: 'Mettre en pause',
  ports: 'Ports',
  networks: 'Réseaux',
  volumes: 'Volumes',
  dependsOn: 'Dépend de',
  env: "Variables d'environnement",
  envShow: 'Afficher les valeurs',
  envHide: 'Masquer les valeurs',
  noAlerts: 'Aucune alerte pour ce service.',
  noData: '—',
};

const SENSITIVE_KEY = /password|secret|token|key|pwd|pass/i;

function maskEnvValue(k: string, v: string, revealed: boolean): string {
  if (revealed || !SENSITIVE_KEY.test(k)) return v;
  return '••••••••';
}

// ── Alert icon helper (mirrors AlertsDashboard) ───────────────────────────────

const ALERT_ICON: Record<Alert['level'], React.ReactNode> = {
  info: <Info size={14} />,
  warning: <AlertTriangle size={14} />,
  critical: <XCircle size={14} />,
};

// ── Master list ───────────────────────────────────────────────────────────────

interface MasterListProps {
  readonly projectId: string;
  readonly services: Service[];
  readonly metrics: ServiceMetrics[] | undefined;
  readonly alerts: Alert[] | undefined;
  readonly selected: string | null;
  readonly onSelect: (name: string) => void;
}

function MasterList({ projectId, services, metrics, alerts, selected, onSelect }: MasterListProps) {
  function handleKeyDown(e: React.KeyboardEvent, name: string) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(name);
    }
  }

  const total = services.length;

  return (
    <div className={styles.master}>
      <div className={styles.masterHeader}>
        <span>{STRINGS.servicesHeader}</span>
        <span>{total}</span>
      </div>
      {total === 0 ? (
        <div className={styles.stateBlock} role="status">
          <Server size={24} />
          <span>{STRINGS.noServices}</span>
          <p className={styles.stateHint}>{STRINGS.noServicesHint}</p>
        </div>
      ) : (
        <ul className={styles.masterList} role="listbox" aria-label={`Services du projet ${projectId}`}>
          {services.map((svc) => {
            const health = deriveServiceHealth(svc.name, metrics, alerts);
            const isSelected = selected === svc.name;
            return (
              <li
                key={svc.name}
                role="option"
                aria-selected={isSelected}
                tabIndex={0}
                className={styles.serviceRow}
                onClick={() => onSelect(svc.name)}
                onKeyDown={(e) => handleKeyDown(e, svc.name)}
              >
                <HealthBadge status={health} compact />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className={styles.serviceRowName}>{svc.name}</div>
                  {svc.image && <div className={styles.serviceRowImage}>{svc.image}</div>}
                </div>
                <ArrowRight
                  size={12}
                  style={{ opacity: isSelected ? 1 : 0, color: 'var(--primary)', flexShrink: 0 }}
                  aria-hidden="true"
                />
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

// ── Service detail ────────────────────────────────────────────────────────────

interface ServiceDetailProps {
  readonly projectId: string;
  readonly service: Service;
  readonly health: HealthStatus;
  readonly metrics: ServiceMetrics | undefined;
  readonly alerts: Alert[];
}

function ServiceDetail({ projectId, service: svc, health, metrics, alerts }: ServiceDetailProps) {
  const { mutate: doAction, isPending } = useServiceAction(projectId);
  const { toast } = useToast();
  const [envExpanded, setEnvExpanded] = useState(false);
  const [envRevealed, setEnvRevealed] = useState(false);

  // reset env state when service changes
  useEffect(() => {
    setEnvExpanded(false);
    setEnvRevealed(false);
  }, [svc.name]);

  function handleAction(action: string, label: string) {
    doAction(
      { service: svc.name, action },
      {
        onSuccess: () => toast(`${label} de ${svc.name} effectué.`, 'success'),
        onError: (err) => toast(`Échec ${label} de ${svc.name} : ${err.message}`, 'error'),
      }
    );
  }

  const isRunning = health === 'running';
  const envEntries = Object.entries(svc.environment);

  return (
    <div className={styles.detail}>
      {/* Header with name + lifecycle actions */}
      <div className={styles.detailHeader}>
        <h2 className={styles.detailTitle}>
          {svc.name}
          {svc.image && <span className={styles.detailImage}>{svc.image}</span>}
        </h2>

        <div className={styles.actions}>
          {/* PRIMARY: Restart (running) or Start (stopped) */}
          {isRunning ? (
            <button
              className={styles.btnPrimary}
              onClick={() => handleAction('restart', STRINGS.restart)}
              disabled={isPending}
              aria-label={`Redémarrer ${svc.name}`}
            >
              <RotateCcw size={14} aria-hidden="true" />
              {STRINGS.restart}
            </button>
          ) : (
            <button
              className={styles.btnPrimary}
              onClick={() => handleAction('start', STRINGS.start)}
              disabled={isPending}
              aria-label={`Démarrer ${svc.name}`}
            >
              <Play size={14} aria-hidden="true" />
              {STRINGS.start}
            </button>
          )}

          {/* SECONDARY: Stop */}
          {isRunning && (
            <button
              className={`${styles.btnSecondary} ${styles.danger}`}
              onClick={() => handleAction('stop', STRINGS.stop)}
              disabled={isPending}
              aria-label={`Arrêter ${svc.name}`}
              title={STRINGS.stop}
            >
              <Square size={14} aria-hidden="true" />
            </button>
          )}

          {/* SECONDARY: Pause */}
          {isRunning && (
            <button
              className={styles.btnSecondary}
              onClick={() => handleAction('pause', STRINGS.pause)}
              disabled={isPending}
              aria-label={`Mettre en pause ${svc.name}`}
              title={STRINGS.pause}
            >
              <Pause size={14} aria-hidden="true" />
            </button>
          )}

          {/* Logs link */}
          <Link
            to={`/projects/${projectId}/logs`}
            className={styles.logLink}
            aria-label={`Voir les logs de ${svc.name}`}
          >
            <ScrollText size={14} aria-hidden="true" />
            {STRINGS.logsLink}
          </Link>
        </div>
      </div>

      {/* Scrollable body */}
      <div className={styles.detailBody}>
        {/* ── Config ── */}
        <section className={styles.section} aria-labelledby="cfg-heading">
          <h3 id="cfg-heading" className={styles.sectionTitle}>
            <Server size={12} aria-hidden="true" />
            {STRINGS.configSection}
          </h3>

          <div className={styles.configGrid}>
            {/* Ports */}
            <div className={styles.configItem}>
              <span className={styles.configLabel}>{STRINGS.ports}</span>
              <div className={styles.configValues}>
                {svc.ports.length > 0 ? (
                  svc.ports.map((p) => (
                    <span key={p} className={styles.badge}>
                      {p}
                    </span>
                  ))
                ) : (
                  <span className={styles.emptyValue}>{STRINGS.noData}</span>
                )}
              </div>
            </div>

            {/* Networks */}
            <div className={styles.configItem}>
              <span className={styles.configLabel}>{STRINGS.networks}</span>
              <div className={styles.configValues}>
                {svc.networks.length > 0 ? (
                  svc.networks.map((n) => (
                    <span key={n} className={styles.badge}>
                      {n}
                    </span>
                  ))
                ) : (
                  <span className={styles.emptyValue}>{STRINGS.noData}</span>
                )}
              </div>
            </div>

            {/* Volumes */}
            {svc.volumes.length > 0 && (
              <div className={styles.configItem}>
                <span className={styles.configLabel}>{STRINGS.volumes}</span>
                <div className={styles.configValues}>
                  {svc.volumes.map((v) => (
                    <span key={v} className={styles.badge}>
                      {v}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Depends on */}
            {svc.depends_on.length > 0 && (
              <div className={styles.configItem}>
                <span className={styles.configLabel}>{STRINGS.dependsOn}</span>
                <div className={styles.configValues}>
                  {svc.depends_on.map((d) => (
                    <span key={d} className={styles.depBadge}>
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Environment variables */}
          {envEntries.length > 0 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <button
                  className={styles.envToggle}
                  onClick={() => setEnvExpanded((v) => !v)}
                  aria-expanded={envExpanded}
                  aria-controls="env-block"
                >
                  {envExpanded ? (
                    <ChevronUp size={12} aria-hidden="true" />
                  ) : (
                    <ChevronDown size={12} aria-hidden="true" />
                  )}
                  {STRINGS.env} ({envEntries.length})
                </button>
                {envExpanded && (
                  <button
                    className={styles.envReveal}
                    onClick={() => setEnvRevealed((v) => !v)}
                    aria-label={envRevealed ? STRINGS.envHide : STRINGS.envShow}
                  >
                    {envRevealed ? <EyeOff size={11} aria-hidden="true" /> : <Eye size={11} aria-hidden="true" />}
                    {envRevealed ? STRINGS.envHide : STRINGS.envShow}
                  </button>
                )}
              </div>
              {envExpanded && (
                <pre id="env-block" className={styles.envPre}>
                  {envEntries.map(([k, v]) => `${k}=${maskEnvValue(k, v, envRevealed)}`).join('\n')}
                </pre>
              )}
            </div>
          )}
        </section>

        {/* ── Metrics sparkline ── */}
        <section className={styles.section} aria-labelledby="metrics-heading">
          <h3 id="metrics-heading" className={styles.sectionTitle}>
            <Cpu size={12} aria-hidden="true" />
            {STRINGS.metricsSection}
          </h3>
          <ServiceSparkline projectId={projectId} serviceName={svc.name} metrics={metrics} />
        </section>

        {/* ── Alerts ── */}
        <section className={styles.section} aria-labelledby="alerts-heading">
          <h3 id="alerts-heading" className={styles.sectionTitle}>
            <AlertTriangle size={12} aria-hidden="true" />
            {STRINGS.alertsSection}
            {alerts.length > 0 && (
              <span
                style={{
                  marginLeft: 'auto',
                  fontSize: 10,
                  padding: '1px 6px',
                  borderRadius: 'var(--radius-full)',
                  background: alerts.some((a) => a.level === 'critical')
                    ? 'var(--status-exited)'
                    : 'var(--status-paused)',
                  color: 'white',
                  fontWeight: 700,
                }}
              >
                {alerts.length}
              </span>
            )}
          </h3>
          <div className={styles.alertsRegion} aria-live="polite" aria-label={`Alertes du service ${svc.name}`}>
            {alerts.length === 0 ? (
              <p className={styles.alertEmpty}>{STRINGS.noAlerts}</p>
            ) : (
              alerts.map((a) => (
                <div key={a.id} className={`${styles.alertItem} ${styles[a.level]}`}>
                  <span
                    style={{
                      flexShrink: 0,
                      color:
                        a.level === 'critical'
                          ? 'var(--status-exited)'
                          : a.level === 'warning'
                            ? 'var(--status-paused)'
                            : 'var(--primary)',
                    }}
                  >
                    {ALERT_ICON[a.level]}
                  </span>
                  <span className={styles.alertMessage}>{a.message}</span>
                  <time className={styles.alertTime} dateTime={a.timestamp}>
                    {new Date(a.timestamp).toLocaleTimeString('fr-FR', { timeStyle: 'short' })}
                  </time>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

// ── Root component ────────────────────────────────────────────────────────────

interface Props {
  readonly projectId: string;
}

export default function ProjectWorkspace({ projectId }: Props) {
  const { data: project, isLoading, error } = useProject(projectId);
  const { data: metrics } = useMetrics(projectId);
  const { data: alerts } = useAlerts();
  const [selectedService, setSelectedService] = useState<string | null>(null);

  // auto-select first service once project loads
  useEffect(() => {
    if (project && !selectedService) {
      setSelectedService(project.services[0]?.name ?? null);
    }
  }, [project, selectedService]);

  const handleSelect = useCallback((name: string) => setSelectedService(name), []);

  if (isLoading) {
    return (
      <div className={styles.workspace}>
        <div className={styles.master}>
          <div className={styles.masterHeader}>
            <span>{STRINGS.servicesHeader}</span>
          </div>
          {/* skeleton rows */}
          {[1, 2, 3, 4].map((n) => (
            <div key={n} className={styles.skeletonRow} role="presentation" aria-hidden="true" />
          ))}
        </div>
        <div className={styles.detail}>
          <div className={styles.detailEmpty} role="status" aria-live="polite">
            <span>{STRINGS.loadingServices}</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className={styles.workspace}>
        <div className={styles.master}>
          <div className={styles.masterHeader}>
            <span>{STRINGS.servicesHeader}</span>
          </div>
          <div className={`${styles.stateBlock} ${styles.stateError}`} role="alert">
            <AlertCircle size={24} />
            <span>{STRINGS.errorServices}</span>
          </div>
        </div>
        <div className={styles.detail}>
          <div className={styles.detailEmpty} />
        </div>
      </div>
    );
  }

  const selectedSvc = project.services.find((s) => s.name === selectedService) ?? null;
  const selectedMetrics = metrics?.find((m) => m.service === selectedService);
  const serviceAlerts = (alerts ?? []).filter((a) => a.project === project.name && a.service === selectedService);
  const selectedHealth = selectedSvc ? deriveServiceHealth(selectedSvc.name, metrics, alerts) : 'unknown';

  return (
    <div className={styles.workspace}>
      <MasterList
        projectId={projectId}
        services={project.services}
        metrics={metrics}
        alerts={alerts}
        selected={selectedService}
        onSelect={handleSelect}
      />

      <div className={styles.detail}>
        {selectedSvc ? (
          <ServiceDetail
            projectId={projectId}
            service={selectedSvc}
            health={selectedHealth}
            metrics={selectedMetrics}
            alerts={serviceAlerts}
          />
        ) : (
          <div className={styles.detailEmpty} role="status">
            <ArrowRight size={28} aria-hidden="true" />
            <span>{STRINGS.selectPrompt}</span>
            <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>{STRINGS.selectHint}</p>
          </div>
        )}
      </div>
    </div>
  );
}
