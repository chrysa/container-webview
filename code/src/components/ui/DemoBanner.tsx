import { useConfigStatus } from '@/domain/config/queries';
import styles from './DemoBanner.module.scss';

const DEMO_MSG = 'Demo mode — exploring with fixture data. No real Docker host or credentials are used.';

/**
 * Persistent amber strip shown at the top of every page while the backend
 * reports `demo_mode`. Hidden entirely when demo mode is off (default).
 */
export function DemoBanner() {
  const { data } = useConfigStatus();

  if (!data?.demo_mode) return null;

  return (
    <div className={styles.banner} role="status" aria-live="polite" data-testid="demo-banner">
      <span className={styles.icon} aria-hidden="true">
        🧪
      </span>
      <span className={styles.message}>
        <strong>DEMO</strong> — {DEMO_MSG}
      </span>
    </div>
  );
}

export default DemoBanner;
