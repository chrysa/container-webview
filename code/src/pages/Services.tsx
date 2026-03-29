import { useParams } from "react-router-dom";
import ServicesTable from "@/features/services/ServicesTable";
import styles from "./ProjectPage.module.scss";

export default function Services() {
  const { projectId } = useParams<{ projectId: string }>();
  if (!projectId) return null;
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.heading}>Services — {projectId}</h1>
      <ServicesTable projectId={projectId} />
    </div>
  );
}
