import { useState } from "react";
import { Play, Square, RotateCcw, Pause, ChevronDown, ChevronUp } from "lucide-react";
import { useProject } from "@/domain/projects/queries";
import { useServiceAction } from "@/domain/lifecycle/queries";
import styles from "./ServicesTable.module.scss";

interface Props {
  projectId: string;
}

export default function ServicesTable({ projectId }: Props) {
  const { data: project, isLoading } = useProject(projectId);
  const { mutate: doAction, isPending } = useServiceAction(projectId);
  const [expanded, setExpanded] = useState<string | null>(null);

  if (isLoading) return <div className={styles.state}>Chargement…</div>;
  if (!project)  return <div className={styles.state}>Projet introuvable.</div>;

  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Service</th>
            <th>Image</th>
            <th>Ports</th>
            <th>Réseaux</th>
            <th>Actions</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {project.services.map((svc) => (
            <>
              <tr key={svc.name} className={styles.row}>
                <td>
                  <span className={styles.name}>{svc.name}</span>
                </td>
                <td className={styles.image}>{svc.image || "—"}</td>
                <td>
                  {svc.ports.length > 0
                    ? svc.ports.map((p) => <span key={p} className={styles.badge}>{p}</span>)
                    : "—"}
                </td>
                <td>
                  {svc.networks.map((n) => <span key={n} className={styles.badge}>{n}</span>)}
                </td>
                <td>
                  <div className={styles.actions}>
                    <button
                      className={`${styles.btn} ${styles.start}`}
                      onClick={() => doAction({ service: svc.name, action: "start" })}
                      disabled={isPending}
                      title="Démarrer"
                    >
                      <Play size={14} />
                    </button>
                    <button
                      className={`${styles.btn} ${styles.stop}`}
                      onClick={() => doAction({ service: svc.name, action: "stop" })}
                      disabled={isPending}
                      title="Arrêter"
                    >
                      <Square size={14} />
                    </button>
                    <button
                      className={`${styles.btn} ${styles.restart}`}
                      onClick={() => doAction({ service: svc.name, action: "restart" })}
                      disabled={isPending}
                      title="Redémarrer"
                    >
                      <RotateCcw size={14} />
                    </button>
                    <button
                      className={`${styles.btn} ${styles.pause}`}
                      onClick={() => doAction({ service: svc.name, action: "pause" })}
                      disabled={isPending}
                      title="Mettre en pause"
                    >
                      <Pause size={14} />
                    </button>
                  </div>
                </td>
                <td>
                  <button
                    className={styles.expandBtn}
                    onClick={() => setExpanded(expanded === svc.name ? null : svc.name)}
                  >
                    {expanded === svc.name ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </td>
              </tr>
              {expanded === svc.name && (
                <tr className={styles.detailRow}>
                  <td colSpan={6}>
                    <div className={styles.detail}>
                      {svc.volumes.length > 0 && (
                        <div>
                          <strong>Volumes :</strong>{" "}
                          {svc.volumes.map((v) => <span key={v} className={styles.badge}>{v}</span>)}
                        </div>
                      )}
                      {Object.keys(svc.environment).length > 0 && (
                        <div>
                          <strong>Variables d&apos;environnement :</strong>
                          <pre className={styles.env}>
                            {Object.entries(svc.environment).map(([k, v]) => `${k}=${v}`).join("\n")}
                          </pre>
                        </div>
                      )}
                      {svc.depends_on.length > 0 && (
                        <div>
                          <strong>Dépend de :</strong>{" "}
                          {svc.depends_on.map((d) => <span key={d} className={styles.badge}>{d}</span>)}
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}
