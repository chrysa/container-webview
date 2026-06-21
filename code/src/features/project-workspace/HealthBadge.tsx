import type { HealthStatus } from '@/domain/health/deriveHealth';
import styles from './HealthBadge.module.scss';

const STRINGS = {
  running: 'actif',
  exited: 'arrêté',
  restarting: 'redémarrage',
  paused: 'pause',
  unhealthy: 'dégradé',
  unknown: 'inconnu',
} satisfies Record<HealthStatus, string>;

interface Props {
  readonly status: HealthStatus;
  /** When true, hides the text label and shows only the dot (compact mode). */
  readonly compact?: boolean;
}

export default function HealthBadge({ status, compact = false }: Props) {
  const label = STRINGS[status];
  return (
    <span className={`${styles.badge} ${styles[status]}`} aria-label={`Statut : ${label}`} title={label}>
      <span className={styles.dot} aria-hidden="true" />
      {!compact && label}
    </span>
  );
}
