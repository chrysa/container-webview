import AlertsDashboard from '@/features/alerts/AlertsDashboard';
import styles from './ProjectPage.module.scss';

export default function Alerts() {
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Alertes</h1>
      <AlertsDashboard />
    </div>
  );
}
