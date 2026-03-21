import { Handle, Position, type NodeProps } from "@xyflow/react";
import styles from "./ServiceNode.module.scss";

interface ServiceData {
  label: string;
  image: string;
  status: string;
  ports: string[];
  statusColor: string;
}

export default function ServiceNode({ data }: NodeProps) {
  const d = data as ServiceData;
  return (
    <div className={styles.node}>
      <Handle type="target" position={Position.Top} />
      <div className={styles.header}>
        <span className={styles.dot} style={{ background: d.statusColor }} />
        <strong className={styles.name}>{d.label}</strong>
      </div>
      {d.image && <div className={styles.image}>{d.image}</div>}
      {d.ports?.length > 0 && (
        <div className={styles.ports}>
          {d.ports.map((p) => (
            <span key={p} className={styles.port}>{p}</span>
          ))}
        </div>
      )}
      <div className={styles.status}>{d.status}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
