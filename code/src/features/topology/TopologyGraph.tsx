import { useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useTopology } from '@/domain/topology/queries';
import ServiceNode from './ServiceNode';
import NetworkNode from './NetworkNode';
import styles from './TopologyGraph.module.scss';

const nodeTypes = {
  service: ServiceNode,
  network: NetworkNode,
};

const STATUS_COLORS: Record<string, string> = {
  running: 'var(--status-running)',
  exited: 'var(--status-exited)',
  paused: 'var(--status-paused)',
  restarting: 'var(--status-restarting)',
  unknown: 'var(--status-unknown)',
};

interface Props {
  projectId: string;
}

export default function TopologyGraph({ projectId }: Props) {
  const { data, isLoading, error } = useTopology(projectId);

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    if (!data) return;
    setNodes(
      data.nodes.map((n) => ({
        id: n.id,
        type: n.type,
        position: n.position,
        data: {
          ...n.data,
          statusColor: STATUS_COLORS[(n.data.status as string) ?? 'unknown'] ?? STATUS_COLORS.unknown,
        },
      }))
    );
    setEdges(
      data.edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label ?? undefined,
        animated: e.animated,
        style: { stroke: 'var(--border-strong)' },
      }))
    );
  }, [data, setNodes, setEdges]);

  if (isLoading) return <div className={styles.state}>Chargement de la topologie…</div>;
  if (error) return <div className={styles.state}>Erreur lors du chargement.</div>;
  if (!data?.nodes.length) return <div className={styles.state}>Aucun service détecté.</div>;

  return (
    <div className={styles.wrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        colorMode="dark"
      >
        <Background />
        <Controls />
        <MiniMap nodeColor={(n) => (n.data as { statusColor?: string }).statusColor ?? '#888'} />
      </ReactFlow>
    </div>
  );
}
