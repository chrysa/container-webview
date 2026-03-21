export interface NodePosition {
  x: number;
  y: number;
}

export interface GraphNode {
  id: string;
  type: string;
  data: {
    label: string;
    image?: string;
    status?: string;
    ports?: string[];
    networks?: string[];
    bgColor?: string;
    color?: string;
  };
  position: NodePosition;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated: boolean;
}

export interface TopologyGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
