import { useParams } from "react-router-dom";
import TopologyGraph from "@/features/topology/TopologyGraph";
import styles from "./ProjectPage.module.scss";

export default function Topology() {
  const { projectId } = useParams<{ projectId: string }>();
  if (!projectId) return null;
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Topologie — {projectId}</h1>
      <TopologyGraph projectId={projectId} />
    </div>
  );
}
