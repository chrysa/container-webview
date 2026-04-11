import { Handle, Position, type NodeProps } from '@xyflow/react';
import styles from './NetworkNode.module.scss';

interface NetworkData {
  label: string;
  color: string;
}

export default function NetworkNode({ data }: NodeProps) {
  const d = data as NetworkData;
  return (
    <div className={styles.node} style={{ borderColor: d.color }}>
      <Handle type="target" position={Position.Top} />
      <span className={styles.icon}>🌐</span>
      <span className={styles.label}>{d.label}</span>
    </div>
  );
}
