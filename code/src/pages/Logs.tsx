import { useParams } from "react-router-dom";
import LogsPanel from "@/features/logs/LogsPanel";
import styles from "./ProjectPage.module.scss";

export default function Logs() {
  const { projectId } = useParams<{ projectId: string }>();
  if (!projectId) return null;
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Logs — {projectId}</h1>
      <LogsPanel projectId={projectId} />
    </div>
  );
}
