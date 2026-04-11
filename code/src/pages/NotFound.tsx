import { Link } from 'react-router-dom';
import styles from './NotFound.module.scss';

export default function NotFound() {
  return (
    <div className={styles.page}>
      <span className={styles.code}>404</span>
      <h1 className={styles.title}>Page introuvable</h1>
      <Link to="/projects" className={styles.back}>
        ← Retour aux projets
      </Link>
    </div>
  );
}
