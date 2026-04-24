import { useParams } from 'react-router-dom';
import LogsPanel from '@/features/logs/LogsPanel';
import { useProject } from '@/domain/projects/queries';
import styles from './ProjectPage.module.scss';

export default function Logs() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: project } = useProject(projectId ?? '');
  if (!projectId) return null;
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Logs — {project?.name ?? projectId}</h1>
      <LogsPanel projectId={projectId} />
    </div>
  );
}
