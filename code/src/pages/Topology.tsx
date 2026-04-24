import { useParams } from 'react-router-dom';
import TopologyGraph from '@/features/topology/TopologyGraph';
import { useProject } from '@/domain/projects/queries';
import styles from './ProjectPage.module.scss';

export default function Topology() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: project } = useProject(projectId ?? '');
  if (!projectId) return null;
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Topologie — {project?.name ?? projectId}</h1>
      <TopologyGraph projectId={projectId} />
    </div>
  );
}
