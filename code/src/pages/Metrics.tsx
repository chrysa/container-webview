import { useParams } from "react-router-dom";
import MetricsCharts from "@/features/metrics/MetricsCharts";
import styles from "./ProjectPage.module.scss";

export default function Metrics() {
  const { projectId } = useParams<{ projectId: string }>();
  if (!projectId) return null;
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Métriques — {projectId}</h1>
      <MetricsCharts projectId={projectId} />
    </div>
  );
}
