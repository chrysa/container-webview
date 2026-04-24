import { AlertTriangle, Info, XCircle, AlertCircle } from 'lucide-react';
import { useAlerts } from '@/domain/alerts/queries';
import type { Alert } from '@/domain/alerts/types';
import styles from './AlertsDashboard.module.scss';

const LEVEL_CONFIG = {
  info: { icon: <Info size={16} />, label: 'Info', cls: 'info' },
  warning: { icon: <AlertTriangle size={16} />, label: 'Warning', cls: 'warning' },
  critical: { icon: <XCircle size={16} />, label: 'Critique', cls: 'critical' },
};

function AlertRow({ alert }: Readonly<{ alert: Alert }>) {
  const cfg = LEVEL_CONFIG[alert.level] ?? LEVEL_CONFIG.info;
  const dateStr = new Date(alert.timestamp).toLocaleString('fr-FR', {
    dateStyle: 'short',
    timeStyle: 'medium',
  });
  return (
    <div className={`${styles.alertRow} ${styles[cfg.cls]}`}>
      <div className={styles.icon}>{cfg.icon}</div>
      <div className={styles.body}>
        <div className={styles.topLine}>
          <span className={styles.level}>{cfg.label}</span>
          <span className={styles.project}>{alert.project}</span>
          <span className={styles.service}>/{alert.service}</span>
        </div>
        <div className={styles.message}>{alert.message}</div>
      </div>
      <div className={styles.time}>{dateStr}</div>
    </div>
  );
}

export default function AlertsDashboard() {
  const { data = [], isLoading, error } = useAlerts();

  const counts = {
    critical: data.filter((a) => a.level === 'critical').length,
    warning: data.filter((a) => a.level === 'warning').length,
    info: data.filter((a) => a.level === 'info').length,
  };

  if (isLoading) return <div className={styles.state}>Chargement des alertes…</div>;
  if (error)
    return (
      <div className={styles.errorState}>
        <AlertCircle size={20} />
        <span>Erreur lors du chargement des alertes.</span>
      </div>
    );
  return (
    <div className={styles.wrapper}>
      <div className={styles.summary}>
        <div className={`${styles.counter} ${styles.critical}`}>
          <XCircle size={20} /> <strong>{counts.critical}</strong> Critique{counts.critical > 1 ? 's' : ''}
        </div>
        <div className={`${styles.counter} ${styles.warning}`}>
          <AlertTriangle size={20} /> <strong>{counts.warning}</strong> Avertissement{counts.warning > 1 ? 's' : ''}
        </div>
        <div className={`${styles.counter} ${styles.info}`}>
          <Info size={20} /> <strong>{counts.info}</strong> Info
        </div>
      </div>

      {data.length === 0 ? (
        <div className={styles.empty}>✅ Aucune alerte active.</div>
      ) : (
        <div className={styles.list}>
          {data.map((alert) => (
            <AlertRow key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </div>
  );
}
